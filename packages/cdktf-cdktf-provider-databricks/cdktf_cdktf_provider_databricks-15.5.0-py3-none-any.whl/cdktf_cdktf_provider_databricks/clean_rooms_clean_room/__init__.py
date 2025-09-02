r'''
# `databricks_clean_rooms_clean_room`

Refer to the Terraform Registry for docs: [`databricks_clean_rooms_clean_room`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room).
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


class CleanRoomsCleanRoom(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoom",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room databricks_clean_rooms_clean_room}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        remote_detailed_info: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room databricks_clean_rooms_clean_room} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#comment CleanRoomsCleanRoom#comment}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#name CleanRoomsCleanRoom#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#owner CleanRoomsCleanRoom#owner}.
        :param remote_detailed_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#remote_detailed_info CleanRoomsCleanRoom#remote_detailed_info}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workspace_id CleanRoomsCleanRoom#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84085888e3ed220a2f3235f74100df7cf2e80b3c1c4e4d00d943c719d3dc7ece)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = CleanRoomsCleanRoomConfig(
            comment=comment,
            name=name,
            owner=owner,
            remote_detailed_info=remote_detailed_info,
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
        '''Generates CDKTF code for importing a CleanRoomsCleanRoom resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CleanRoomsCleanRoom to import.
        :param import_from_id: The id of the existing CleanRoomsCleanRoom that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CleanRoomsCleanRoom to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d5532a1a56c959f9dac9402c9054c52a1dbc371c26106e1507c7dc825515f42)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRemoteDetailedInfo")
    def put_remote_detailed_info(
        self,
        *,
        cloud_vendor: typing.Optional[builtins.str] = None,
        collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoCollaborators", typing.Dict[builtins.str, typing.Any]]]]] = None,
        egress_network_policy: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_vendor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#cloud_vendor CleanRoomsCleanRoom#cloud_vendor}.
        :param collaborators: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborators CleanRoomsCleanRoom#collaborators}.
        :param egress_network_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#egress_network_policy CleanRoomsCleanRoom#egress_network_policy}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#region CleanRoomsCleanRoom#region}.
        '''
        value = CleanRoomsCleanRoomRemoteDetailedInfo(
            cloud_vendor=cloud_vendor,
            collaborators=collaborators,
            egress_network_policy=egress_network_policy,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putRemoteDetailedInfo", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetRemoteDetailedInfo")
    def reset_remote_detailed_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteDetailedInfo", []))

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
    @jsii.member(jsii_name="accessRestricted")
    def access_restricted(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessRestricted"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="localCollaboratorAlias")
    def local_collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localCollaboratorAlias"))

    @builtins.property
    @jsii.member(jsii_name="outputCatalog")
    def output_catalog(self) -> "CleanRoomsCleanRoomOutputCatalogOutputReference":
        return typing.cast("CleanRoomsCleanRoomOutputCatalogOutputReference", jsii.get(self, "outputCatalog"))

    @builtins.property
    @jsii.member(jsii_name="remoteDetailedInfo")
    def remote_detailed_info(
        self,
    ) -> "CleanRoomsCleanRoomRemoteDetailedInfoOutputReference":
        return typing.cast("CleanRoomsCleanRoomRemoteDetailedInfoOutputReference", jsii.get(self, "remoteDetailedInfo"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteDetailedInfoInput")
    def remote_detailed_info_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomsCleanRoomRemoteDetailedInfo"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CleanRoomsCleanRoomRemoteDetailedInfo"]], jsii.get(self, "remoteDetailedInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c77e891a1a27185797dc06a483e17492f0e0e66dea736f2b608d46061263905)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03299fd5834307d95bbdc36059da9545f3a6ab2f325e2a3beaae8e867b912d40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94d6230f1eb7e67560f1dbe4e4239a7d4a6034aeb58603da9718b0e9cd4817a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4e76518b7059ded9c8838bce026220e2189806f5b18976405b989e2ab190c4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "comment": "comment",
        "name": "name",
        "owner": "owner",
        "remote_detailed_info": "remoteDetailedInfo",
        "workspace_id": "workspaceId",
    },
)
class CleanRoomsCleanRoomConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        comment: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        remote_detailed_info: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfo", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#comment CleanRoomsCleanRoom#comment}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#name CleanRoomsCleanRoom#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#owner CleanRoomsCleanRoom#owner}.
        :param remote_detailed_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#remote_detailed_info CleanRoomsCleanRoom#remote_detailed_info}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workspace_id CleanRoomsCleanRoom#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(remote_detailed_info, dict):
            remote_detailed_info = CleanRoomsCleanRoomRemoteDetailedInfo(**remote_detailed_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba5e380f4c1eeecbe20d78482a09c64830f64d4b002e59ef54f994bbb8212d67)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument remote_detailed_info", value=remote_detailed_info, expected_type=type_hints["remote_detailed_info"])
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
        if comment is not None:
            self._values["comment"] = comment
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if remote_detailed_info is not None:
            self._values["remote_detailed_info"] = remote_detailed_info
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
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#comment CleanRoomsCleanRoom#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#name CleanRoomsCleanRoom#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#owner CleanRoomsCleanRoom#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_detailed_info(
        self,
    ) -> typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#remote_detailed_info CleanRoomsCleanRoom#remote_detailed_info}.'''
        result = self._values.get("remote_detailed_info")
        return typing.cast(typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfo"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workspace_id CleanRoomsCleanRoom#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomOutputCatalog",
    jsii_struct_bases=[],
    name_mapping={"catalog_name": "catalogName"},
)
class CleanRoomsCleanRoomOutputCatalog:
    def __init__(self, *, catalog_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#catalog_name CleanRoomsCleanRoom#catalog_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f3bd32c6ef1e23d375cefd226fb4b9139b34215320d8bd992a8525c1731082e)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#catalog_name CleanRoomsCleanRoom#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomOutputCatalog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomOutputCatalogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomOutputCatalogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c44453b8737485c6553e8a1428f92f9bf8ee19d04ee2eef3a9d9e6b3613c7cf9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCatalogName")
    def reset_catalog_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalogName", []))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="catalogNameInput")
    def catalog_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogNameInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogName")
    def catalog_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalogName"))

    @catalog_name.setter
    def catalog_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9731c28f6d6dd160669e2ef8ed72c65fadf3c56fe15ca7179831b11fd8a090df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CleanRoomsCleanRoomOutputCatalog]:
        return typing.cast(typing.Optional[CleanRoomsCleanRoomOutputCatalog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomsCleanRoomOutputCatalog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286d2d7f0abefd55aa5195da80667742daf4550f6a57084e24dd1f8702cf0eab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfo",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_vendor": "cloudVendor",
        "collaborators": "collaborators",
        "egress_network_policy": "egressNetworkPolicy",
        "region": "region",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfo:
    def __init__(
        self,
        *,
        cloud_vendor: typing.Optional[builtins.str] = None,
        collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoCollaborators", typing.Dict[builtins.str, typing.Any]]]]] = None,
        egress_network_policy: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_vendor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#cloud_vendor CleanRoomsCleanRoom#cloud_vendor}.
        :param collaborators: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborators CleanRoomsCleanRoom#collaborators}.
        :param egress_network_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#egress_network_policy CleanRoomsCleanRoom#egress_network_policy}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#region CleanRoomsCleanRoom#region}.
        '''
        if isinstance(egress_network_policy, dict):
            egress_network_policy = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy(**egress_network_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bd215e5e810663ab0ceffc45c9c123015998f49e8533c0c851a18a4517d4903)
            check_type(argname="argument cloud_vendor", value=cloud_vendor, expected_type=type_hints["cloud_vendor"])
            check_type(argname="argument collaborators", value=collaborators, expected_type=type_hints["collaborators"])
            check_type(argname="argument egress_network_policy", value=egress_network_policy, expected_type=type_hints["egress_network_policy"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_vendor is not None:
            self._values["cloud_vendor"] = cloud_vendor
        if collaborators is not None:
            self._values["collaborators"] = collaborators
        if egress_network_policy is not None:
            self._values["egress_network_policy"] = egress_network_policy
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def cloud_vendor(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#cloud_vendor CleanRoomsCleanRoom#cloud_vendor}.'''
        result = self._values.get("cloud_vendor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collaborators(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoCollaborators"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborators CleanRoomsCleanRoom#collaborators}.'''
        result = self._values.get("collaborators")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoCollaborators"]]], result)

    @builtins.property
    def egress_network_policy(
        self,
    ) -> typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#egress_network_policy CleanRoomsCleanRoom#egress_network_policy}.'''
        result = self._values.get("egress_network_policy")
        return typing.cast(typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy"], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#region CleanRoomsCleanRoom#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoCollaborators",
    jsii_struct_bases=[],
    name_mapping={
        "collaborator_alias": "collaboratorAlias",
        "global_metastore_id": "globalMetastoreId",
        "invite_recipient_email": "inviteRecipientEmail",
        "invite_recipient_workspace_id": "inviteRecipientWorkspaceId",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoCollaborators:
    def __init__(
        self,
        *,
        collaborator_alias: builtins.str,
        global_metastore_id: typing.Optional[builtins.str] = None,
        invite_recipient_email: typing.Optional[builtins.str] = None,
        invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborator_alias CleanRoomsCleanRoom#collaborator_alias}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#global_metastore_id CleanRoomsCleanRoom#global_metastore_id}.
        :param invite_recipient_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_email CleanRoomsCleanRoom#invite_recipient_email}.
        :param invite_recipient_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_workspace_id CleanRoomsCleanRoom#invite_recipient_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__588709c5ce76bfdeca34fedec8442fe7e78ed68519e44771d0b13f6ab1e725cb)
            check_type(argname="argument collaborator_alias", value=collaborator_alias, expected_type=type_hints["collaborator_alias"])
            check_type(argname="argument global_metastore_id", value=global_metastore_id, expected_type=type_hints["global_metastore_id"])
            check_type(argname="argument invite_recipient_email", value=invite_recipient_email, expected_type=type_hints["invite_recipient_email"])
            check_type(argname="argument invite_recipient_workspace_id", value=invite_recipient_workspace_id, expected_type=type_hints["invite_recipient_workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "collaborator_alias": collaborator_alias,
        }
        if global_metastore_id is not None:
            self._values["global_metastore_id"] = global_metastore_id
        if invite_recipient_email is not None:
            self._values["invite_recipient_email"] = invite_recipient_email
        if invite_recipient_workspace_id is not None:
            self._values["invite_recipient_workspace_id"] = invite_recipient_workspace_id

    @builtins.property
    def collaborator_alias(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborator_alias CleanRoomsCleanRoom#collaborator_alias}.'''
        result = self._values.get("collaborator_alias")
        assert result is not None, "Required property 'collaborator_alias' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#global_metastore_id CleanRoomsCleanRoom#global_metastore_id}.'''
        result = self._values.get("global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_email CleanRoomsCleanRoom#invite_recipient_email}.'''
        result = self._values.get("invite_recipient_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_workspace_id CleanRoomsCleanRoom#invite_recipient_workspace_id}.'''
        result = self._values.get("invite_recipient_workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoCollaborators(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0f7ea180a47ebb98746585a2f82db26e75956f6803f0dc13636e8c0a58ecb9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddc0046fdc2fe6f8d3de94d2e10db4273eed6361330446ebae8f21aae404a28b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be07a33caada09565a3ffc739e22bc25fbf486f257dac18c7400904b58cfd8f8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__359e99803c245c8f20495c99a665c80273c890bea5250ab116d2d8de01049a5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92bd39e6e27399c47cb69718cada96ef9190dfab8681ec6aed1b08d823d26b07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c81aaf09b7eb5761eb55897661b74dbdfbb09a61a35456752329bb3d3abe6c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__891fb04cc830e06f6e9b63e799fa681e8c3a90cb490a2da00889288173bbba2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetGlobalMetastoreId")
    def reset_global_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalMetastoreId", []))

    @jsii.member(jsii_name="resetInviteRecipientEmail")
    def reset_invite_recipient_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteRecipientEmail", []))

    @jsii.member(jsii_name="resetInviteRecipientWorkspaceId")
    def reset_invite_recipient_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteRecipientWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @builtins.property
    @jsii.member(jsii_name="organizationName")
    def organization_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationName"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorAliasInput")
    def collaborator_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collaboratorAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreIdInput")
    def global_metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalMetastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmailInput")
    def invite_recipient_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inviteRecipientEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceIdInput")
    def invite_recipient_workspace_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "inviteRecipientWorkspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorAlias")
    def collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collaboratorAlias"))

    @collaborator_alias.setter
    def collaborator_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__985180d7cca53cd6a640a6c51c76f28db474d49ec27838a4a1b424f213d639d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreId")
    def global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalMetastoreId"))

    @global_metastore_id.setter
    def global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5927b8183a14847411ab525d781ea290391cdd33217929cf28ba7362c0718264)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalMetastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmail")
    def invite_recipient_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inviteRecipientEmail"))

    @invite_recipient_email.setter
    def invite_recipient_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2fa9cb202a61f206679b7a60d7df9c7683fd397afe2e080f3f1068ba6b8efe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceId")
    def invite_recipient_workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inviteRecipientWorkspaceId"))

    @invite_recipient_workspace_id.setter
    def invite_recipient_workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eac8d02ab3872bd7bca99de82fe4059bd2004b2076c4a1ac2e6cbfee6edc8b62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a597b843ad815dcc35f991d7ac1060177d49cc3c3c6d4622acd5c9acedf8c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile",
    jsii_struct_bases=[],
    name_mapping={
        "compliance_standards": "complianceStandards",
        "is_enabled": "isEnabled",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile:
    def __init__(
        self,
        *,
        compliance_standards: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param compliance_standards: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#compliance_standards CleanRoomsCleanRoom#compliance_standards}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#is_enabled CleanRoomsCleanRoom#is_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4526e20b7d67d0edbf5b71752482e60befdf40f5fcc709b6e468182d78bdbe02)
            check_type(argname="argument compliance_standards", value=compliance_standards, expected_type=type_hints["compliance_standards"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if compliance_standards is not None:
            self._values["compliance_standards"] = compliance_standards
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def compliance_standards(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#compliance_standards CleanRoomsCleanRoom#compliance_standards}.'''
        result = self._values.get("compliance_standards")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#is_enabled CleanRoomsCleanRoom#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58c94aeb2a5f897efa980700038b9fd7c7fa7019f27f737ce2f6fadb628d2de7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetComplianceStandards")
    def reset_compliance_standards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplianceStandards", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="complianceStandardsInput")
    def compliance_standards_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "complianceStandardsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="complianceStandards")
    def compliance_standards(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "complianceStandards"))

    @compliance_standards.setter
    def compliance_standards(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__904d84c99fb17366471092a8ece5ec07e926f8a047a884ceb84f1ed0fc1e3257)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complianceStandards", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__422dadcbce4bd13fd8e6b0031250e512a544b496a343cc546d8035ef5da6d0c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile]:
        return typing.cast(typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad079e74492fbb5a054f650d56202ea586297b4ac4093bb9637679c697ee6c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoCreator",
    jsii_struct_bases=[],
    name_mapping={
        "collaborator_alias": "collaboratorAlias",
        "global_metastore_id": "globalMetastoreId",
        "invite_recipient_email": "inviteRecipientEmail",
        "invite_recipient_workspace_id": "inviteRecipientWorkspaceId",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoCreator:
    def __init__(
        self,
        *,
        collaborator_alias: builtins.str,
        global_metastore_id: typing.Optional[builtins.str] = None,
        invite_recipient_email: typing.Optional[builtins.str] = None,
        invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborator_alias CleanRoomsCleanRoom#collaborator_alias}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#global_metastore_id CleanRoomsCleanRoom#global_metastore_id}.
        :param invite_recipient_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_email CleanRoomsCleanRoom#invite_recipient_email}.
        :param invite_recipient_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_workspace_id CleanRoomsCleanRoom#invite_recipient_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7868f47695d93b8c8f17beffb3ebccfa7d81d1e49a7d96bef449ff20d23a88af)
            check_type(argname="argument collaborator_alias", value=collaborator_alias, expected_type=type_hints["collaborator_alias"])
            check_type(argname="argument global_metastore_id", value=global_metastore_id, expected_type=type_hints["global_metastore_id"])
            check_type(argname="argument invite_recipient_email", value=invite_recipient_email, expected_type=type_hints["invite_recipient_email"])
            check_type(argname="argument invite_recipient_workspace_id", value=invite_recipient_workspace_id, expected_type=type_hints["invite_recipient_workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "collaborator_alias": collaborator_alias,
        }
        if global_metastore_id is not None:
            self._values["global_metastore_id"] = global_metastore_id
        if invite_recipient_email is not None:
            self._values["invite_recipient_email"] = invite_recipient_email
        if invite_recipient_workspace_id is not None:
            self._values["invite_recipient_workspace_id"] = invite_recipient_workspace_id

    @builtins.property
    def collaborator_alias(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#collaborator_alias CleanRoomsCleanRoom#collaborator_alias}.'''
        result = self._values.get("collaborator_alias")
        assert result is not None, "Required property 'collaborator_alias' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#global_metastore_id CleanRoomsCleanRoom#global_metastore_id}.'''
        result = self._values.get("global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_email CleanRoomsCleanRoom#invite_recipient_email}.'''
        result = self._values.get("invite_recipient_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#invite_recipient_workspace_id CleanRoomsCleanRoom#invite_recipient_workspace_id}.'''
        result = self._values.get("invite_recipient_workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoCreator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoCreatorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoCreatorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5abef0168acdea5377ca9e619d7879a3179562d287fa6024f144192bc36e1332)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGlobalMetastoreId")
    def reset_global_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalMetastoreId", []))

    @jsii.member(jsii_name="resetInviteRecipientEmail")
    def reset_invite_recipient_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteRecipientEmail", []))

    @jsii.member(jsii_name="resetInviteRecipientWorkspaceId")
    def reset_invite_recipient_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInviteRecipientWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @builtins.property
    @jsii.member(jsii_name="organizationName")
    def organization_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationName"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorAliasInput")
    def collaborator_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collaboratorAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreIdInput")
    def global_metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalMetastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmailInput")
    def invite_recipient_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inviteRecipientEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceIdInput")
    def invite_recipient_workspace_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "inviteRecipientWorkspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorAlias")
    def collaborator_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collaboratorAlias"))

    @collaborator_alias.setter
    def collaborator_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__769b15e7a59a05299a6e4bbf45b68edeb596ac2e4ee1c75d0aba3ae1d53a5795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreId")
    def global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalMetastoreId"))

    @global_metastore_id.setter
    def global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fb3b50debc5a5a77308703d9adda447e4a30a997f37f92b7e71971892a648f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalMetastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmail")
    def invite_recipient_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inviteRecipientEmail"))

    @invite_recipient_email.setter
    def invite_recipient_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2091f4cca24f33e58ef28873084ae36a13f1834c4f5ff6d5c88bf48118a8e41a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceId")
    def invite_recipient_workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inviteRecipientWorkspaceId"))

    @invite_recipient_workspace_id.setter
    def invite_recipient_workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9c9edd8e29fc50158b23b743c2d01b39db5d5cd539635905575afaac2308a42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoCreator]:
        return typing.cast(typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoCreator], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoCreator],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fde9875be54b9ff362555d129925d4ed0133dd2fbd6ce8468569dc1ef5dd6a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy",
    jsii_struct_bases=[],
    name_mapping={"internet_access": "internetAccess"},
)
class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy:
    def __init__(
        self,
        *,
        internet_access: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internet_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#internet_access CleanRoomsCleanRoom#internet_access}.
        '''
        if isinstance(internet_access, dict):
            internet_access = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess(**internet_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bef79bf580d66521ac46870b1e6c0988102da076dd1fb4fbae174b909c07287)
            check_type(argname="argument internet_access", value=internet_access, expected_type=type_hints["internet_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if internet_access is not None:
            self._values["internet_access"] = internet_access

    @builtins.property
    def internet_access(
        self,
    ) -> typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#internet_access CleanRoomsCleanRoom#internet_access}.'''
        result = self._values.get("internet_access")
        return typing.cast(typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_internet_destinations": "allowedInternetDestinations",
        "allowed_storage_destinations": "allowedStorageDestinations",
        "log_only_mode": "logOnlyMode",
        "restriction_mode": "restrictionMode",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess:
    def __init__(
        self,
        *,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        log_only_mode: typing.Optional[typing.Union["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode", typing.Dict[builtins.str, typing.Any]]] = None,
        restriction_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_internet_destinations CleanRoomsCleanRoom#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_storage_destinations CleanRoomsCleanRoom#allowed_storage_destinations}.
        :param log_only_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode CleanRoomsCleanRoom#log_only_mode}.
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#restriction_mode CleanRoomsCleanRoom#restriction_mode}.
        '''
        if isinstance(log_only_mode, dict):
            log_only_mode = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(**log_only_mode)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e143f72372acd77a2713959c70f81e3cd14cf8889a6b7197b71f0da927be86e)
            check_type(argname="argument allowed_internet_destinations", value=allowed_internet_destinations, expected_type=type_hints["allowed_internet_destinations"])
            check_type(argname="argument allowed_storage_destinations", value=allowed_storage_destinations, expected_type=type_hints["allowed_storage_destinations"])
            check_type(argname="argument log_only_mode", value=log_only_mode, expected_type=type_hints["log_only_mode"])
            check_type(argname="argument restriction_mode", value=restriction_mode, expected_type=type_hints["restriction_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_internet_destinations is not None:
            self._values["allowed_internet_destinations"] = allowed_internet_destinations
        if allowed_storage_destinations is not None:
            self._values["allowed_storage_destinations"] = allowed_storage_destinations
        if log_only_mode is not None:
            self._values["log_only_mode"] = log_only_mode
        if restriction_mode is not None:
            self._values["restriction_mode"] = restriction_mode

    @builtins.property
    def allowed_internet_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_internet_destinations CleanRoomsCleanRoom#allowed_internet_destinations}.'''
        result = self._values.get("allowed_internet_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations"]]], result)

    @builtins.property
    def allowed_storage_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_storage_destinations CleanRoomsCleanRoom#allowed_storage_destinations}.'''
        result = self._values.get("allowed_storage_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations"]]], result)

    @builtins.property
    def log_only_mode(
        self,
    ) -> typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode CleanRoomsCleanRoom#log_only_mode}.'''
        result = self._values.get("log_only_mode")
        return typing.cast(typing.Optional["CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode"], result)

    @builtins.property
    def restriction_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#restriction_mode CleanRoomsCleanRoom#restriction_mode}.'''
        result = self._values.get("restriction_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "protocol": "protocol",
        "type": "type",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations:
    def __init__(
        self,
        *,
        destination: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#destination CleanRoomsCleanRoom#destination}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#protocol CleanRoomsCleanRoom#protocol}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#type CleanRoomsCleanRoom#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbb2ccd9a458ee32bfb8839d0c4502c998291d1600c92d72f1287b5ad3c72734)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if protocol is not None:
            self._values["protocol"] = protocol
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def destination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#destination CleanRoomsCleanRoom#destination}.'''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#protocol CleanRoomsCleanRoom#protocol}.'''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#type CleanRoomsCleanRoom#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35efb0daea425581c5683df3405dd1d5e504f1a945701c66598536fa969ebc38)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d5e0a1ad40cbc0d79f22e5d8dfb22d7a48a388dd9ec8542b49506aa8b488d6d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93a08bba9daa543b7f345d171edeb49a2a9d3930514ab4f0482f90b6bc7fc2d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d13638f6cc0466aa1b6397c9ef58aee25c963b7a7057eeb22ee22fd999baa9ed)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82c9518e0d54023ae8fbc927ac4bf9222639764dd656d0b1c34511233ba64075)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__033fb9d8976b24aa0369300eceb1a3e1651309d40d9251f1a67f069fb610dd00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ba712bba12ef242f1d718261ff3ffbfb113c0fbbccaa5e3ac76aff86f21447a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae30fe86cf3c77f2b2a8bbb687577328cb9e613b9884e92fae726b4bb4ac4b9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d52a9f7c28044fc42fa60fb48cc6de5ac957003bcf947ab86b87e7653aa9d88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86588b9c4a8b55c6ecd40a416dca137e2d84afe0c32bace28add55a1f024f48c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b14b3636fb579cf85b3822deb754df91ada120134945f4f579632cb40db989)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_paths": "allowedPaths",
        "azure_container": "azureContainer",
        "azure_dns_zone": "azureDnsZone",
        "azure_storage_account": "azureStorageAccount",
        "azure_storage_service": "azureStorageService",
        "bucket_name": "bucketName",
        "region": "region",
        "type": "type",
    },
)
class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations:
    def __init__(
        self,
        *,
        allowed_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        azure_container: typing.Optional[builtins.str] = None,
        azure_dns_zone: typing.Optional[builtins.str] = None,
        azure_storage_account: typing.Optional[builtins.str] = None,
        azure_storage_service: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_paths: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_paths CleanRoomsCleanRoom#allowed_paths}.
        :param azure_container: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_container CleanRoomsCleanRoom#azure_container}.
        :param azure_dns_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_dns_zone CleanRoomsCleanRoom#azure_dns_zone}.
        :param azure_storage_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_storage_account CleanRoomsCleanRoom#azure_storage_account}.
        :param azure_storage_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_storage_service CleanRoomsCleanRoom#azure_storage_service}.
        :param bucket_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#bucket_name CleanRoomsCleanRoom#bucket_name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#region CleanRoomsCleanRoom#region}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#type CleanRoomsCleanRoom#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c5edae53c3905e48b85368600fd2e959c3a1b471c1fc7aab3a8dbafe8b01bc7)
            check_type(argname="argument allowed_paths", value=allowed_paths, expected_type=type_hints["allowed_paths"])
            check_type(argname="argument azure_container", value=azure_container, expected_type=type_hints["azure_container"])
            check_type(argname="argument azure_dns_zone", value=azure_dns_zone, expected_type=type_hints["azure_dns_zone"])
            check_type(argname="argument azure_storage_account", value=azure_storage_account, expected_type=type_hints["azure_storage_account"])
            check_type(argname="argument azure_storage_service", value=azure_storage_service, expected_type=type_hints["azure_storage_service"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_paths is not None:
            self._values["allowed_paths"] = allowed_paths
        if azure_container is not None:
            self._values["azure_container"] = azure_container
        if azure_dns_zone is not None:
            self._values["azure_dns_zone"] = azure_dns_zone
        if azure_storage_account is not None:
            self._values["azure_storage_account"] = azure_storage_account
        if azure_storage_service is not None:
            self._values["azure_storage_service"] = azure_storage_service
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if region is not None:
            self._values["region"] = region
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def allowed_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_paths CleanRoomsCleanRoom#allowed_paths}.'''
        result = self._values.get("allowed_paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def azure_container(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_container CleanRoomsCleanRoom#azure_container}.'''
        result = self._values.get("azure_container")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_dns_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_dns_zone CleanRoomsCleanRoom#azure_dns_zone}.'''
        result = self._values.get("azure_dns_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_storage_account CleanRoomsCleanRoom#azure_storage_account}.'''
        result = self._values.get("azure_storage_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#azure_storage_service CleanRoomsCleanRoom#azure_storage_service}.'''
        result = self._values.get("azure_storage_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#bucket_name CleanRoomsCleanRoom#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#region CleanRoomsCleanRoom#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#type CleanRoomsCleanRoom#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__273cb745c360665dd1938e02e8b576b960f5026e167290b6839662366ac768e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90c330c2d257f2e1ec6a865a891367d7ffaee77705801427bfd98a8a72e34125)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1395ccb1bc47feeabb70b6faef308d4fbbfe0d080d2534f6672a0d0af22bc076)
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
            type_hints = typing.get_type_hints(_typecheckingstub__029790a59a3613f954c049c136e7b8cc0d4f697058ee1401fe6fbcdb6869195e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbeaa34fab11b744ef89d0438f05f3d07d7765a0230e4793ba3ca41d964d41b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4659142deb9c752c96f88a2ad95867597ee47a1492be24d8f14a709c8084fe4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__321867690d097c89f8cec55adf9261d692eca4bf62b260443d07d32c8e8b7f4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowedPaths")
    def reset_allowed_paths(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedPaths", []))

    @jsii.member(jsii_name="resetAzureContainer")
    def reset_azure_container(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureContainer", []))

    @jsii.member(jsii_name="resetAzureDnsZone")
    def reset_azure_dns_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureDnsZone", []))

    @jsii.member(jsii_name="resetAzureStorageAccount")
    def reset_azure_storage_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageAccount", []))

    @jsii.member(jsii_name="resetAzureStorageService")
    def reset_azure_storage_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageService", []))

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedPathsInput")
    def allowed_paths_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedPathsInput"))

    @builtins.property
    @jsii.member(jsii_name="azureContainerInput")
    def azure_container_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureContainerInput"))

    @builtins.property
    @jsii.member(jsii_name="azureDnsZoneInput")
    def azure_dns_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureDnsZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccountInput")
    def azure_storage_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageServiceInput")
    def azure_storage_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedPaths")
    def allowed_paths(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedPaths"))

    @allowed_paths.setter
    def allowed_paths(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08138b8153f4363e8db6e2d713b761935df103d16e6197f4ac495ff14b5636c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedPaths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureContainer")
    def azure_container(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureContainer"))

    @azure_container.setter
    def azure_container(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47fcd238bae1cae31755075f2264d36f990648c4a3f9e4bdc5ff5bcf5efb0acd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureContainer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureDnsZone")
    def azure_dns_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureDnsZone"))

    @azure_dns_zone.setter
    def azure_dns_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28a3eb005b8e58c2d371838e6791a56f33e4f833b225f07a614a60aac8c36a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureDnsZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccount")
    def azure_storage_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageAccount"))

    @azure_storage_account.setter
    def azure_storage_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6f7cb81cb7038b34dcf7ce50bbc0e3111e160e24a06133e666bde7ddd09a47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageService")
    def azure_storage_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageService"))

    @azure_storage_service.setter
    def azure_storage_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d282665c47e988601bc8e1d05553902db67976abd7376f85180041d4f1d87572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f32841d8c6e8356e4ec23cf3ad5136b010aab95b40f76226f05782260e4511e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f11f1effb217260ed5eb3ff3cb7b67c651f183d5c9657819eb5442ae44052dc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b3a6bc442b8567ed73b7c7827271511afef7c0583efcc5785c25f88c00aa7c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f55d1dac40a7652e24ba9c05ef8e55d0398cb9722df358a5429e48082eda7a5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode",
    jsii_struct_bases=[],
    name_mapping={"log_only_mode_type": "logOnlyModeType", "workloads": "workloads"},
)
class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode:
    def __init__(
        self,
        *,
        log_only_mode_type: typing.Optional[builtins.str] = None,
        workloads: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param log_only_mode_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode_type CleanRoomsCleanRoom#log_only_mode_type}.
        :param workloads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workloads CleanRoomsCleanRoom#workloads}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2b1d53ffd810c765f532af53e7bf8b52f6ec0adc05b93c52c34e9a0d28b3244)
            check_type(argname="argument log_only_mode_type", value=log_only_mode_type, expected_type=type_hints["log_only_mode_type"])
            check_type(argname="argument workloads", value=workloads, expected_type=type_hints["workloads"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_only_mode_type is not None:
            self._values["log_only_mode_type"] = log_only_mode_type
        if workloads is not None:
            self._values["workloads"] = workloads

    @builtins.property
    def log_only_mode_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode_type CleanRoomsCleanRoom#log_only_mode_type}.'''
        result = self._values.get("log_only_mode_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workloads(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workloads CleanRoomsCleanRoom#workloads}.'''
        result = self._values.get("workloads")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e4e14da961bbfb1299cdc3d09608d9cc8c31ba8435b4b1b3fa90dc58a24cff1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLogOnlyModeType")
    def reset_log_only_mode_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogOnlyModeType", []))

    @jsii.member(jsii_name="resetWorkloads")
    def reset_workloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloads", []))

    @builtins.property
    @jsii.member(jsii_name="logOnlyModeTypeInput")
    def log_only_mode_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logOnlyModeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadsInput")
    def workloads_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "workloadsInput"))

    @builtins.property
    @jsii.member(jsii_name="logOnlyModeType")
    def log_only_mode_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logOnlyModeType"))

    @log_only_mode_type.setter
    def log_only_mode_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e160787b3a5a72fe39c90f01f5225697bcf2747da3200d83199685259552d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logOnlyModeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloads")
    def workloads(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "workloads"))

    @workloads.setter
    def workloads(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed152d10f16ab05460253c0c2f16a20eaa8b23739b8a1fd13fdbd599f818ca6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da485e4363121fbfcad3486e19481d6f864e6710cab69f9e225c21eaed6073ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15532da5d63c63b4e4711118fd452cdf3631891b089a560220116db086fcb68d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAllowedInternetDestinations")
    def put_allowed_internet_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a665f67fb6afaf1fa730051cfbd9294e9a5b7afdcd9d901745a5d21402dd3cc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedInternetDestinations", [value]))

    @jsii.member(jsii_name="putAllowedStorageDestinations")
    def put_allowed_storage_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2fb06b7bb5a6609aabef0aff19cf6eee9f0453f5dcdd70904bbed875932fb50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedStorageDestinations", [value]))

    @jsii.member(jsii_name="putLogOnlyMode")
    def put_log_only_mode(
        self,
        *,
        log_only_mode_type: typing.Optional[builtins.str] = None,
        workloads: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param log_only_mode_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode_type CleanRoomsCleanRoom#log_only_mode_type}.
        :param workloads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#workloads CleanRoomsCleanRoom#workloads}.
        '''
        value = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(
            log_only_mode_type=log_only_mode_type, workloads=workloads
        )

        return typing.cast(None, jsii.invoke(self, "putLogOnlyMode", [value]))

    @jsii.member(jsii_name="resetAllowedInternetDestinations")
    def reset_allowed_internet_destinations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedInternetDestinations", []))

    @jsii.member(jsii_name="resetAllowedStorageDestinations")
    def reset_allowed_storage_destinations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedStorageDestinations", []))

    @jsii.member(jsii_name="resetLogOnlyMode")
    def reset_log_only_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogOnlyMode", []))

    @jsii.member(jsii_name="resetRestrictionMode")
    def reset_restriction_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictionMode", []))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinations")
    def allowed_internet_destinations(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList, jsii.get(self, "allowedInternetDestinations"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinations")
    def allowed_storage_destinations(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList, jsii.get(self, "allowedStorageDestinations"))

    @builtins.property
    @jsii.member(jsii_name="logOnlyMode")
    def log_only_mode(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference, jsii.get(self, "logOnlyMode"))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinationsInput")
    def allowed_internet_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]], jsii.get(self, "allowedInternetDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinationsInput")
    def allowed_storage_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]], jsii.get(self, "allowedStorageDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="logOnlyModeInput")
    def log_only_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]], jsii.get(self, "logOnlyModeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictionModeInput")
    def restriction_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restrictionModeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictionMode")
    def restriction_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restrictionMode"))

    @restriction_mode.setter
    def restriction_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a9efe23d7b18c36b65502fa51a1e7661feae04afbcfafde0f4110b9a68f9e1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e07fcfed99b613bedc427a4b824e92a63918c022e8feea5a13bbb7ceaada260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f12f851c0e32d548d35ec3f63f7d50fa85d084021f7cc8ee5c65f802b8786336)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInternetAccess")
    def put_internet_access(
        self,
        *,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        log_only_mode: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode, typing.Dict[builtins.str, typing.Any]]] = None,
        restriction_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_internet_destinations CleanRoomsCleanRoom#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#allowed_storage_destinations CleanRoomsCleanRoom#allowed_storage_destinations}.
        :param log_only_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#log_only_mode CleanRoomsCleanRoom#log_only_mode}.
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#restriction_mode CleanRoomsCleanRoom#restriction_mode}.
        '''
        value = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess(
            allowed_internet_destinations=allowed_internet_destinations,
            allowed_storage_destinations=allowed_storage_destinations,
            log_only_mode=log_only_mode,
            restriction_mode=restriction_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putInternetAccess", [value]))

    @jsii.member(jsii_name="resetInternetAccess")
    def reset_internet_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternetAccess", []))

    @builtins.property
    @jsii.member(jsii_name="internetAccess")
    def internet_access(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference, jsii.get(self, "internetAccess"))

    @builtins.property
    @jsii.member(jsii_name="internetAccessInput")
    def internet_access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]], jsii.get(self, "internetAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffc3d6a98f81d52e1323c847221b6c4aa149e16af9fb014899a65989c50e48ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CleanRoomsCleanRoomRemoteDetailedInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.cleanRoomsCleanRoom.CleanRoomsCleanRoomRemoteDetailedInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9af41e17052dbb26bb8cb20ff6717199f252c1f574f36b11b90dc8aa81ed4671)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCollaborators")
    def put_collaborators(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8a580d860f2b7b7c3e2c7b9191592e0b90869d65bc55e3740b0b758e09cacc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCollaborators", [value]))

    @jsii.member(jsii_name="putEgressNetworkPolicy")
    def put_egress_network_policy(
        self,
        *,
        internet_access: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internet_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/clean_rooms_clean_room#internet_access CleanRoomsCleanRoom#internet_access}.
        '''
        value = CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy(
            internet_access=internet_access
        )

        return typing.cast(None, jsii.invoke(self, "putEgressNetworkPolicy", [value]))

    @jsii.member(jsii_name="resetCloudVendor")
    def reset_cloud_vendor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudVendor", []))

    @jsii.member(jsii_name="resetCollaborators")
    def reset_collaborators(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollaborators", []))

    @jsii.member(jsii_name="resetEgressNetworkPolicy")
    def reset_egress_network_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressNetworkPolicy", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="centralCleanRoomId")
    def central_clean_room_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "centralCleanRoomId"))

    @builtins.property
    @jsii.member(jsii_name="collaborators")
    def collaborators(self) -> CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsList:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsList, jsii.get(self, "collaborators"))

    @builtins.property
    @jsii.member(jsii_name="complianceSecurityProfile")
    def compliance_security_profile(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfileOutputReference:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfileOutputReference, jsii.get(self, "complianceSecurityProfile"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(self) -> CleanRoomsCleanRoomRemoteDetailedInfoCreatorOutputReference:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoCreatorOutputReference, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="egressNetworkPolicy")
    def egress_network_policy(
        self,
    ) -> CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyOutputReference:
        return typing.cast(CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyOutputReference, jsii.get(self, "egressNetworkPolicy"))

    @builtins.property
    @jsii.member(jsii_name="cloudVendorInput")
    def cloud_vendor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudVendorInput"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorsInput")
    def collaborators_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]], jsii.get(self, "collaboratorsInput"))

    @builtins.property
    @jsii.member(jsii_name="egressNetworkPolicyInput")
    def egress_network_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]], jsii.get(self, "egressNetworkPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudVendor")
    def cloud_vendor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudVendor"))

    @cloud_vendor.setter
    def cloud_vendor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0e80b0468dfeaaafcb1e1d1bc8128710417b68aa2ac22733ebf4385a8293ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudVendor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5d29dbafc259bbec25ce199e653d45f67cc56d0f3487ee21d381ade9ce5708f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b272af1470ebbcdf693f2404da704d9bb26b18960be2309b8abaa227dbd24262)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CleanRoomsCleanRoom",
    "CleanRoomsCleanRoomConfig",
    "CleanRoomsCleanRoomOutputCatalog",
    "CleanRoomsCleanRoomOutputCatalogOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfo",
    "CleanRoomsCleanRoomRemoteDetailedInfoCollaborators",
    "CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsList",
    "CleanRoomsCleanRoomRemoteDetailedInfoCollaboratorsOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile",
    "CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfileOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoCreator",
    "CleanRoomsCleanRoomRemoteDetailedInfoCreatorOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyOutputReference",
    "CleanRoomsCleanRoomRemoteDetailedInfoOutputReference",
]

publication.publish()

def _typecheckingstub__84085888e3ed220a2f3235f74100df7cf2e80b3c1c4e4d00d943c719d3dc7ece(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    remote_detailed_info: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfo, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__5d5532a1a56c959f9dac9402c9054c52a1dbc371c26106e1507c7dc825515f42(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c77e891a1a27185797dc06a483e17492f0e0e66dea736f2b608d46061263905(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03299fd5834307d95bbdc36059da9545f3a6ab2f325e2a3beaae8e867b912d40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94d6230f1eb7e67560f1dbe4e4239a7d4a6034aeb58603da9718b0e9cd4817a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e76518b7059ded9c8838bce026220e2189806f5b18976405b989e2ab190c4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba5e380f4c1eeecbe20d78482a09c64830f64d4b002e59ef54f994bbb8212d67(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    comment: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    remote_detailed_info: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f3bd32c6ef1e23d375cefd226fb4b9139b34215320d8bd992a8525c1731082e(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c44453b8737485c6553e8a1428f92f9bf8ee19d04ee2eef3a9d9e6b3613c7cf9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9731c28f6d6dd160669e2ef8ed72c65fadf3c56fe15ca7179831b11fd8a090df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286d2d7f0abefd55aa5195da80667742daf4550f6a57084e24dd1f8702cf0eab(
    value: typing.Optional[CleanRoomsCleanRoomOutputCatalog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd215e5e810663ab0ceffc45c9c123015998f49e8533c0c851a18a4517d4903(
    *,
    cloud_vendor: typing.Optional[builtins.str] = None,
    collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]]] = None,
    egress_network_policy: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__588709c5ce76bfdeca34fedec8442fe7e78ed68519e44771d0b13f6ab1e725cb(
    *,
    collaborator_alias: builtins.str,
    global_metastore_id: typing.Optional[builtins.str] = None,
    invite_recipient_email: typing.Optional[builtins.str] = None,
    invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f7ea180a47ebb98746585a2f82db26e75956f6803f0dc13636e8c0a58ecb9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddc0046fdc2fe6f8d3de94d2e10db4273eed6361330446ebae8f21aae404a28b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be07a33caada09565a3ffc739e22bc25fbf486f257dac18c7400904b58cfd8f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__359e99803c245c8f20495c99a665c80273c890bea5250ab116d2d8de01049a5f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92bd39e6e27399c47cb69718cada96ef9190dfab8681ec6aed1b08d823d26b07(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c81aaf09b7eb5761eb55897661b74dbdfbb09a61a35456752329bb3d3abe6c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__891fb04cc830e06f6e9b63e799fa681e8c3a90cb490a2da00889288173bbba2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__985180d7cca53cd6a640a6c51c76f28db474d49ec27838a4a1b424f213d639d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5927b8183a14847411ab525d781ea290391cdd33217929cf28ba7362c0718264(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2fa9cb202a61f206679b7a60d7df9c7683fd397afe2e080f3f1068ba6b8efe5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac8d02ab3872bd7bca99de82fe4059bd2004b2076c4a1ac2e6cbfee6edc8b62(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a597b843ad815dcc35f991d7ac1060177d49cc3c3c6d4622acd5c9acedf8c2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoCollaborators]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4526e20b7d67d0edbf5b71752482e60befdf40f5fcc709b6e468182d78bdbe02(
    *,
    compliance_standards: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c94aeb2a5f897efa980700038b9fd7c7fa7019f27f737ce2f6fadb628d2de7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__904d84c99fb17366471092a8ece5ec07e926f8a047a884ceb84f1ed0fc1e3257(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__422dadcbce4bd13fd8e6b0031250e512a544b496a343cc546d8035ef5da6d0c2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad079e74492fbb5a054f650d56202ea586297b4ac4093bb9637679c697ee6c1(
    value: typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoComplianceSecurityProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7868f47695d93b8c8f17beffb3ebccfa7d81d1e49a7d96bef449ff20d23a88af(
    *,
    collaborator_alias: builtins.str,
    global_metastore_id: typing.Optional[builtins.str] = None,
    invite_recipient_email: typing.Optional[builtins.str] = None,
    invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5abef0168acdea5377ca9e619d7879a3179562d287fa6024f144192bc36e1332(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__769b15e7a59a05299a6e4bbf45b68edeb596ac2e4ee1c75d0aba3ae1d53a5795(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fb3b50debc5a5a77308703d9adda447e4a30a997f37f92b7e71971892a648f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2091f4cca24f33e58ef28873084ae36a13f1834c4f5ff6d5c88bf48118a8e41a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9c9edd8e29fc50158b23b743c2d01b39db5d5cd539635905575afaac2308a42(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fde9875be54b9ff362555d129925d4ed0133dd2fbd6ce8468569dc1ef5dd6a3(
    value: typing.Optional[CleanRoomsCleanRoomRemoteDetailedInfoCreator],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bef79bf580d66521ac46870b1e6c0988102da076dd1fb4fbae174b909c07287(
    *,
    internet_access: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e143f72372acd77a2713959c70f81e3cd14cf8889a6b7197b71f0da927be86e(
    *,
    allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    log_only_mode: typing.Optional[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode, typing.Dict[builtins.str, typing.Any]]] = None,
    restriction_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbb2ccd9a458ee32bfb8839d0c4502c998291d1600c92d72f1287b5ad3c72734(
    *,
    destination: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35efb0daea425581c5683df3405dd1d5e504f1a945701c66598536fa969ebc38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5e0a1ad40cbc0d79f22e5d8dfb22d7a48a388dd9ec8542b49506aa8b488d6d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93a08bba9daa543b7f345d171edeb49a2a9d3930514ab4f0482f90b6bc7fc2d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d13638f6cc0466aa1b6397c9ef58aee25c963b7a7057eeb22ee22fd999baa9ed(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82c9518e0d54023ae8fbc927ac4bf9222639764dd656d0b1c34511233ba64075(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__033fb9d8976b24aa0369300eceb1a3e1651309d40d9251f1a67f069fb610dd00(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba712bba12ef242f1d718261ff3ffbfb113c0fbbccaa5e3ac76aff86f21447a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae30fe86cf3c77f2b2a8bbb687577328cb9e613b9884e92fae726b4bb4ac4b9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d52a9f7c28044fc42fa60fb48cc6de5ac957003bcf947ab86b87e7653aa9d88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86588b9c4a8b55c6ecd40a416dca137e2d84afe0c32bace28add55a1f024f48c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b14b3636fb579cf85b3822deb754df91ada120134945f4f579632cb40db989(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c5edae53c3905e48b85368600fd2e959c3a1b471c1fc7aab3a8dbafe8b01bc7(
    *,
    allowed_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
    azure_container: typing.Optional[builtins.str] = None,
    azure_dns_zone: typing.Optional[builtins.str] = None,
    azure_storage_account: typing.Optional[builtins.str] = None,
    azure_storage_service: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__273cb745c360665dd1938e02e8b576b960f5026e167290b6839662366ac768e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90c330c2d257f2e1ec6a865a891367d7ffaee77705801427bfd98a8a72e34125(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1395ccb1bc47feeabb70b6faef308d4fbbfe0d080d2534f6672a0d0af22bc076(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__029790a59a3613f954c049c136e7b8cc0d4f697058ee1401fe6fbcdb6869195e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbeaa34fab11b744ef89d0438f05f3d07d7765a0230e4793ba3ca41d964d41b8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4659142deb9c752c96f88a2ad95867597ee47a1492be24d8f14a709c8084fe4f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__321867690d097c89f8cec55adf9261d692eca4bf62b260443d07d32c8e8b7f4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08138b8153f4363e8db6e2d713b761935df103d16e6197f4ac495ff14b5636c1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47fcd238bae1cae31755075f2264d36f990648c4a3f9e4bdc5ff5bcf5efb0acd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a3eb005b8e58c2d371838e6791a56f33e4f833b225f07a614a60aac8c36a15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6f7cb81cb7038b34dcf7ce50bbc0e3111e160e24a06133e666bde7ddd09a47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d282665c47e988601bc8e1d05553902db67976abd7376f85180041d4f1d87572(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f32841d8c6e8356e4ec23cf3ad5136b010aab95b40f76226f05782260e4511e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f11f1effb217260ed5eb3ff3cb7b67c651f183d5c9657819eb5442ae44052dc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b3a6bc442b8567ed73b7c7827271511afef7c0583efcc5785c25f88c00aa7c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f55d1dac40a7652e24ba9c05ef8e55d0398cb9722df358a5429e48082eda7a5f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b1d53ffd810c765f532af53e7bf8b52f6ec0adc05b93c52c34e9a0d28b3244(
    *,
    log_only_mode_type: typing.Optional[builtins.str] = None,
    workloads: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e4e14da961bbfb1299cdc3d09608d9cc8c31ba8435b4b1b3fa90dc58a24cff1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e160787b3a5a72fe39c90f01f5225697bcf2747da3200d83199685259552d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed152d10f16ab05460253c0c2f16a20eaa8b23739b8a1fd13fdbd599f818ca6b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da485e4363121fbfcad3486e19481d6f864e6710cab69f9e225c21eaed6073ed(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15532da5d63c63b4e4711118fd452cdf3631891b089a560220116db086fcb68d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a665f67fb6afaf1fa730051cfbd9294e9a5b7afdcd9d901745a5d21402dd3cc9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fb06b7bb5a6609aabef0aff19cf6eee9f0453f5dcdd70904bbed875932fb50(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a9efe23d7b18c36b65502fa51a1e7661feae04afbcfafde0f4110b9a68f9e1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e07fcfed99b613bedc427a4b824e92a63918c022e8feea5a13bbb7ceaada260(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicyInternetAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f12f851c0e32d548d35ec3f63f7d50fa85d084021f7cc8ee5c65f802b8786336(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffc3d6a98f81d52e1323c847221b6c4aa149e16af9fb014899a65989c50e48ad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfoEgressNetworkPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9af41e17052dbb26bb8cb20ff6717199f252c1f574f36b11b90dc8aa81ed4671(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8a580d860f2b7b7c3e2c7b9191592e0b90869d65bc55e3740b0b758e09cacc4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CleanRoomsCleanRoomRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e80b0468dfeaaafcb1e1d1bc8128710417b68aa2ac22733ebf4385a8293ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5d29dbafc259bbec25ce199e653d45f67cc56d0f3487ee21d381ade9ce5708f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b272af1470ebbcdf693f2404da704d9bb26b18960be2309b8abaa227dbd24262(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CleanRoomsCleanRoomRemoteDetailedInfo]],
) -> None:
    """Type checking stubs"""
    pass
