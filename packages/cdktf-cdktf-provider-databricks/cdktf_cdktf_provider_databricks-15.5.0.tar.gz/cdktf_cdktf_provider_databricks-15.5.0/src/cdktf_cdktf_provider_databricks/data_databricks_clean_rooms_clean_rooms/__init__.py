r'''
# `data_databricks_clean_rooms_clean_rooms`

Refer to the Terraform Registry for docs: [`data_databricks_clean_rooms_clean_rooms`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms).
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


class DataDatabricksCleanRoomsCleanRooms(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRooms",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms databricks_clean_rooms_clean_rooms}.'''

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
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms databricks_clean_rooms_clean_rooms} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workspace_id DataDatabricksCleanRoomsCleanRooms#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f3aafd18900f7c44f08832226142021e04d995ccbd768cb00e02598e8d1146)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksCleanRoomsCleanRoomsConfig(
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
        '''Generates CDKTF code for importing a DataDatabricksCleanRoomsCleanRooms resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksCleanRoomsCleanRooms to import.
        :param import_from_id: The id of the existing DataDatabricksCleanRoomsCleanRooms that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksCleanRoomsCleanRooms to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be5e23783e1852455e5b7eab3b81661415fca6212ff6bde7afd0d126f2ccfdc1)
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
    @jsii.member(jsii_name="cleanRooms")
    def clean_rooms(self) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsList":
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsList", jsii.get(self, "cleanRooms"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__6616dfeaf723842d331be7439c69561653a2c94df6fd9671f7a1eeaf9159d02c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRooms",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "name": "name",
        "owner": "owner",
        "remote_detailed_info": "remoteDetailedInfo",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRooms:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        remote_detailed_info: typing.Optional[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#comment DataDatabricksCleanRoomsCleanRooms#comment}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#name DataDatabricksCleanRoomsCleanRooms#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#owner DataDatabricksCleanRoomsCleanRooms#owner}.
        :param remote_detailed_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#remote_detailed_info DataDatabricksCleanRoomsCleanRooms#remote_detailed_info}.
        '''
        if isinstance(remote_detailed_info, dict):
            remote_detailed_info = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo(**remote_detailed_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__478ceb53cd30b96107b7f82519eb12628c67388bccf11efa8a800c493db3b787)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument remote_detailed_info", value=remote_detailed_info, expected_type=type_hints["remote_detailed_info"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if remote_detailed_info is not None:
            self._values["remote_detailed_info"] = remote_detailed_info

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#comment DataDatabricksCleanRoomsCleanRooms#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#name DataDatabricksCleanRoomsCleanRooms#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#owner DataDatabricksCleanRoomsCleanRooms#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_detailed_info(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#remote_detailed_info DataDatabricksCleanRoomsCleanRooms#remote_detailed_info}.'''
        result = self._values.get("remote_detailed_info")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRooms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c9418b58fb0a8962578e8449edc127542c28f838e135bc2bee101d42a3c6e0f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54bda2c4299fa77751535902bf710df3ac853501a77cc07c4912836b4ab4673b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98ab75df8db891a48d9be940babfc46a5cfb5518a7056becf83bc9fc43a0142a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd11eb5405787fae797f480af70c6d83033f157bbbc37264957066becd5665a5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__19e93c1233d8193f35111c68f0ffa1d637523fe74863e724a9fef05f0148c674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRooms]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRooms]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRooms]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c9836042c1d2426e9172b0d03815f4bdf91ae10d72730216a35fec03c4a79e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog",
    jsii_struct_bases=[],
    name_mapping={"catalog_name": "catalogName"},
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog:
    def __init__(self, *, catalog_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param catalog_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#catalog_name DataDatabricksCleanRoomsCleanRooms#catalog_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84bc7dd7eacb8b9c521d006fd1c5d6a00ce59516d3667c6b97e8848001ab0720)
            check_type(argname="argument catalog_name", value=catalog_name, expected_type=type_hints["catalog_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog_name is not None:
            self._values["catalog_name"] = catalog_name

    @builtins.property
    def catalog_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#catalog_name DataDatabricksCleanRoomsCleanRooms#catalog_name}.'''
        result = self._values.get("catalog_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39510785446f5680940d754b2d8ea69f1471bee503523c1b2c5b005cf5dce24b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16bd911a7ad76c3c5e2585c38e8dc7530d9e7e19f9e080f8f761f51100dd0a72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalogName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a7798574d79cdec8812ed314735d6e7b8f50e23846491c90a6ff1aec058f42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6a80a85ce78cc124c137524fdd053f3765bebef1a486d5fc3f16127f19c4b53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRemoteDetailedInfo")
    def put_remote_detailed_info(
        self,
        *,
        cloud_vendor: typing.Optional[builtins.str] = None,
        collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators", typing.Dict[builtins.str, typing.Any]]]]] = None,
        egress_network_policy: typing.Optional[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_vendor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#cloud_vendor DataDatabricksCleanRoomsCleanRooms#cloud_vendor}.
        :param collaborators: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborators DataDatabricksCleanRoomsCleanRooms#collaborators}.
        :param egress_network_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#egress_network_policy DataDatabricksCleanRoomsCleanRooms#egress_network_policy}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#region DataDatabricksCleanRoomsCleanRooms#region}.
        '''
        value = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo(
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
    def output_catalog(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalogOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalogOutputReference, jsii.get(self, "outputCatalog"))

    @builtins.property
    @jsii.member(jsii_name="remoteDetailedInfo")
    def remote_detailed_info(
        self,
    ) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoOutputReference":
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoOutputReference", jsii.get(self, "remoteDetailedInfo"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo"]], jsii.get(self, "remoteDetailedInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c8d2466d71978538da54df6b4ad16e6cd5fe033cb3b101175123db73dc34db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__487da3ddbd10c8002f4738dcfdb5ba167554e14b240176bbaf843327111efd51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a99d30e20f81fcff0863199f245cff471f0bbad6c87ae1d5a0564f7c4f9e994e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRooms]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRooms], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRooms],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca272b8e72746c1844671673a2bb84bb951003b096958a2db2d9a769ca3d3b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_vendor": "cloudVendor",
        "collaborators": "collaborators",
        "egress_network_policy": "egressNetworkPolicy",
        "region": "region",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo:
    def __init__(
        self,
        *,
        cloud_vendor: typing.Optional[builtins.str] = None,
        collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators", typing.Dict[builtins.str, typing.Any]]]]] = None,
        egress_network_policy: typing.Optional[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_vendor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#cloud_vendor DataDatabricksCleanRoomsCleanRooms#cloud_vendor}.
        :param collaborators: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborators DataDatabricksCleanRoomsCleanRooms#collaborators}.
        :param egress_network_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#egress_network_policy DataDatabricksCleanRoomsCleanRooms#egress_network_policy}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#region DataDatabricksCleanRoomsCleanRooms#region}.
        '''
        if isinstance(egress_network_policy, dict):
            egress_network_policy = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy(**egress_network_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20718e11a0b5a4d9651928599ef15f429677c932c89083206a015ce4f18a34e7)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#cloud_vendor DataDatabricksCleanRoomsCleanRooms#cloud_vendor}.'''
        result = self._values.get("cloud_vendor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collaborators(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborators DataDatabricksCleanRoomsCleanRooms#collaborators}.'''
        result = self._values.get("collaborators")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators"]]], result)

    @builtins.property
    def egress_network_policy(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#egress_network_policy DataDatabricksCleanRoomsCleanRooms#egress_network_policy}.'''
        result = self._values.get("egress_network_policy")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy"], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#region DataDatabricksCleanRoomsCleanRooms#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators",
    jsii_struct_bases=[],
    name_mapping={
        "collaborator_alias": "collaboratorAlias",
        "global_metastore_id": "globalMetastoreId",
        "invite_recipient_email": "inviteRecipientEmail",
        "invite_recipient_workspace_id": "inviteRecipientWorkspaceId",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators:
    def __init__(
        self,
        *,
        collaborator_alias: builtins.str,
        global_metastore_id: typing.Optional[builtins.str] = None,
        invite_recipient_email: typing.Optional[builtins.str] = None,
        invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborator_alias DataDatabricksCleanRoomsCleanRooms#collaborator_alias}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#global_metastore_id DataDatabricksCleanRoomsCleanRooms#global_metastore_id}.
        :param invite_recipient_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_email DataDatabricksCleanRoomsCleanRooms#invite_recipient_email}.
        :param invite_recipient_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_workspace_id DataDatabricksCleanRoomsCleanRooms#invite_recipient_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3487afbe1327c29205b157decfc96d292804fcabfe2cd6401137d4bfb94b341e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborator_alias DataDatabricksCleanRoomsCleanRooms#collaborator_alias}.'''
        result = self._values.get("collaborator_alias")
        assert result is not None, "Required property 'collaborator_alias' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#global_metastore_id DataDatabricksCleanRoomsCleanRooms#global_metastore_id}.'''
        result = self._values.get("global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_email DataDatabricksCleanRoomsCleanRooms#invite_recipient_email}.'''
        result = self._values.get("invite_recipient_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_workspace_id DataDatabricksCleanRoomsCleanRooms#invite_recipient_workspace_id}.'''
        result = self._values.get("invite_recipient_workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__550d83b31fed3bc690c48164a479b1dfd6f984a8d61546275b2f5ebe411c0fff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30d3785070b50aadf959192bacfbded564835845c6ce6d9f6fc38f315be63c0c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e5ea6662001874ab2c42a37f45ae9f1e352e27c085303a21862590bbfe280c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cea3b541a78286025fae20a4590a57c98684ebebfad5f3af0844f0bdd23d7b0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__893d195d8de65fedc65a82a7aecce2d4561f6826edc8af2eecfa0cc4fa6c6822)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a84992589354dd4c40f07b7d72f9cb7c6782eb4c1bcd603e1ad1c695a54a887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf7dd8b35d12536f1695eb3bfb583c50a73f1db0910cdf91da24348faf114879)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f1af3ecd5ae5d6cc29fc824b341a0f4039afa3eb89779165aefce4d0a7de3b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreId")
    def global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalMetastoreId"))

    @global_metastore_id.setter
    def global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da57eebe273b8f55ea4ffa1c2bae86c8d40854b0490f4cea53812f41167f0c32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalMetastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmail")
    def invite_recipient_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inviteRecipientEmail"))

    @invite_recipient_email.setter
    def invite_recipient_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0db32cc4ea5179fcffffdd1c10ae73982db6b6cc71cf5b2fc9125dfe8f4b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceId")
    def invite_recipient_workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inviteRecipientWorkspaceId"))

    @invite_recipient_workspace_id.setter
    def invite_recipient_workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e81e7a68205e85e99358d3c3f055d861b12d84027d1226704c4e80b3282e994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ef9d0cb3de1765a6aa9fbf6e0d2ee63a6fe6fb7549047a1b0b4a31914e4740d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile",
    jsii_struct_bases=[],
    name_mapping={
        "compliance_standards": "complianceStandards",
        "is_enabled": "isEnabled",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile:
    def __init__(
        self,
        *,
        compliance_standards: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param compliance_standards: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#compliance_standards DataDatabricksCleanRoomsCleanRooms#compliance_standards}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#is_enabled DataDatabricksCleanRoomsCleanRooms#is_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36deb36896f5bba8ab33116d9e7798380bbbfb99f9efd58b4f710160fb96456e)
            check_type(argname="argument compliance_standards", value=compliance_standards, expected_type=type_hints["compliance_standards"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if compliance_standards is not None:
            self._values["compliance_standards"] = compliance_standards
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def compliance_standards(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#compliance_standards DataDatabricksCleanRoomsCleanRooms#compliance_standards}.'''
        result = self._values.get("compliance_standards")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#is_enabled DataDatabricksCleanRoomsCleanRooms#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__863fe03f1b02653c44f0a96b2046cea7a3484e98d6bb64f55634ca66476c9bff)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f54499724e246e58760d3d1a38bcff2714198882a7eb53c0690db4c769840b5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e4f91ac00f049125d2d37f94b5643aecf5e6e84e043c28518cde1e79024fd671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4035687518a2fa64cbefa496f76cb150ba676037c6c1cbb204b46e27cbeaaf10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator",
    jsii_struct_bases=[],
    name_mapping={
        "collaborator_alias": "collaboratorAlias",
        "global_metastore_id": "globalMetastoreId",
        "invite_recipient_email": "inviteRecipientEmail",
        "invite_recipient_workspace_id": "inviteRecipientWorkspaceId",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator:
    def __init__(
        self,
        *,
        collaborator_alias: builtins.str,
        global_metastore_id: typing.Optional[builtins.str] = None,
        invite_recipient_email: typing.Optional[builtins.str] = None,
        invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param collaborator_alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborator_alias DataDatabricksCleanRoomsCleanRooms#collaborator_alias}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#global_metastore_id DataDatabricksCleanRoomsCleanRooms#global_metastore_id}.
        :param invite_recipient_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_email DataDatabricksCleanRoomsCleanRooms#invite_recipient_email}.
        :param invite_recipient_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_workspace_id DataDatabricksCleanRoomsCleanRooms#invite_recipient_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de194aea49c02e9fcc2c3df6a057d575b1042db1b2200bdee11a2bc88cfdb9ff)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#collaborator_alias DataDatabricksCleanRoomsCleanRooms#collaborator_alias}.'''
        result = self._values.get("collaborator_alias")
        assert result is not None, "Required property 'collaborator_alias' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#global_metastore_id DataDatabricksCleanRoomsCleanRooms#global_metastore_id}.'''
        result = self._values.get("global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_email DataDatabricksCleanRoomsCleanRooms#invite_recipient_email}.'''
        result = self._values.get("invite_recipient_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invite_recipient_workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#invite_recipient_workspace_id DataDatabricksCleanRoomsCleanRooms#invite_recipient_workspace_id}.'''
        result = self._values.get("invite_recipient_workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreatorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreatorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__774a351e8282cb8c4ec31c299e96cddb0a039d9d8a9beb927064a8c1fa0d8cf7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d62e65e356c0bf9528c5d99022ec825fe761bb943a1dab4ef0e029de32f0da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collaboratorAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreId")
    def global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalMetastoreId"))

    @global_metastore_id.setter
    def global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf7759b4cbe297812b2b63479e729f09f3fd7489f916fceb9174ff5319d5de5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalMetastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientEmail")
    def invite_recipient_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inviteRecipientEmail"))

    @invite_recipient_email.setter
    def invite_recipient_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__336314cab889ce14d395dc4fe1b9d8eeec8a2769ed8005dbd1ffc3557d38e129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inviteRecipientWorkspaceId")
    def invite_recipient_workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inviteRecipientWorkspaceId"))

    @invite_recipient_workspace_id.setter
    def invite_recipient_workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__527fd489a67dad7b5b88fb1d8c6b467207180b967dab93d385e6b3faaa0c1801)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inviteRecipientWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator]:
        return typing.cast(typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a801916a6c9b072da2522cdc079c9a7e595a50d37b6bf74d950c36f578580bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy",
    jsii_struct_bases=[],
    name_mapping={"internet_access": "internetAccess"},
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy:
    def __init__(
        self,
        *,
        internet_access: typing.Optional[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internet_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#internet_access DataDatabricksCleanRoomsCleanRooms#internet_access}.
        '''
        if isinstance(internet_access, dict):
            internet_access = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess(**internet_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59b440184889ac954709ed22eff8a50ecf388c100ebade934aeb5fde0f5a8a65)
            check_type(argname="argument internet_access", value=internet_access, expected_type=type_hints["internet_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if internet_access is not None:
            self._values["internet_access"] = internet_access

    @builtins.property
    def internet_access(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#internet_access DataDatabricksCleanRoomsCleanRooms#internet_access}.'''
        result = self._values.get("internet_access")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_internet_destinations": "allowedInternetDestinations",
        "allowed_storage_destinations": "allowedStorageDestinations",
        "log_only_mode": "logOnlyMode",
        "restriction_mode": "restrictionMode",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess:
    def __init__(
        self,
        *,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        log_only_mode: typing.Optional[typing.Union["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode", typing.Dict[builtins.str, typing.Any]]] = None,
        restriction_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_internet_destinations DataDatabricksCleanRoomsCleanRooms#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_storage_destinations DataDatabricksCleanRoomsCleanRooms#allowed_storage_destinations}.
        :param log_only_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode DataDatabricksCleanRoomsCleanRooms#log_only_mode}.
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#restriction_mode DataDatabricksCleanRoomsCleanRooms#restriction_mode}.
        '''
        if isinstance(log_only_mode, dict):
            log_only_mode = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(**log_only_mode)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0f8f323eed631878748713af16907f33712498950b2bfdda5eaedd036366ba2)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_internet_destinations DataDatabricksCleanRoomsCleanRooms#allowed_internet_destinations}.'''
        result = self._values.get("allowed_internet_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations"]]], result)

    @builtins.property
    def allowed_storage_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_storage_destinations DataDatabricksCleanRoomsCleanRooms#allowed_storage_destinations}.'''
        result = self._values.get("allowed_storage_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations"]]], result)

    @builtins.property
    def log_only_mode(
        self,
    ) -> typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode DataDatabricksCleanRoomsCleanRooms#log_only_mode}.'''
        result = self._values.get("log_only_mode")
        return typing.cast(typing.Optional["DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode"], result)

    @builtins.property
    def restriction_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#restriction_mode DataDatabricksCleanRoomsCleanRooms#restriction_mode}.'''
        result = self._values.get("restriction_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "protocol": "protocol",
        "type": "type",
    },
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations:
    def __init__(
        self,
        *,
        destination: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#destination DataDatabricksCleanRoomsCleanRooms#destination}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#protocol DataDatabricksCleanRoomsCleanRooms#protocol}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#type DataDatabricksCleanRoomsCleanRooms#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cfe5d88d97e4b957d872e72717f9996c112c6e4112adbb0a6d98bdd3685b273)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#destination DataDatabricksCleanRoomsCleanRooms#destination}.'''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#protocol DataDatabricksCleanRoomsCleanRooms#protocol}.'''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#type DataDatabricksCleanRoomsCleanRooms#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69a4f234b3906535b49b1439453432e597ce08e243a2108e41b67306df502d4d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c77c2af1b1950e6b2975ca1d163553e690ca4133a4816e35d9488abd51cd22e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724e617a11f645ba9712273f1fbfb262765682f4c9ee62c5ada2117c896f9c7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9b1c6a83357ea448ed136312b33452098f9fa9c40bc1b4f80a472e86b123703)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d56cef0cac71be7842771a29b730ebbff3cfe75d5432820389553e1e7c7fddf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac069716c5959e28c49f257210a4012b575c72a8301d3e97864f3d27ef21f856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b1c8556a53fc4798c7efcdaa9be64fadbb46213006b403b2e680248a5780791)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1120131196ce3d3b1552274dda2a080340fcd979d4f523d3f37a5ea53b219f60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a097cb271415331e8109d60084894354d431ff735a7d638b2eafa15fb6730708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__662cce819dd309177fe167005854cbd3cad1fc3b34b8de88a0244f128905c0f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211b16a76c59b002d4d19de01810b6603c0d8be5699c6430e1f1113ae4b9017d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations",
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
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations:
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
        :param allowed_paths: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_paths DataDatabricksCleanRoomsCleanRooms#allowed_paths}.
        :param azure_container: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_container DataDatabricksCleanRoomsCleanRooms#azure_container}.
        :param azure_dns_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_dns_zone DataDatabricksCleanRoomsCleanRooms#azure_dns_zone}.
        :param azure_storage_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_storage_account DataDatabricksCleanRoomsCleanRooms#azure_storage_account}.
        :param azure_storage_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_storage_service DataDatabricksCleanRoomsCleanRooms#azure_storage_service}.
        :param bucket_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#bucket_name DataDatabricksCleanRoomsCleanRooms#bucket_name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#region DataDatabricksCleanRoomsCleanRooms#region}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#type DataDatabricksCleanRoomsCleanRooms#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad21d3171097fd8894d3b57c397993517aeb213167b8001f22c3aa0924ee23fb)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_paths DataDatabricksCleanRoomsCleanRooms#allowed_paths}.'''
        result = self._values.get("allowed_paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def azure_container(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_container DataDatabricksCleanRoomsCleanRooms#azure_container}.'''
        result = self._values.get("azure_container")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_dns_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_dns_zone DataDatabricksCleanRoomsCleanRooms#azure_dns_zone}.'''
        result = self._values.get("azure_dns_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_storage_account DataDatabricksCleanRoomsCleanRooms#azure_storage_account}.'''
        result = self._values.get("azure_storage_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#azure_storage_service DataDatabricksCleanRoomsCleanRooms#azure_storage_service}.'''
        result = self._values.get("azure_storage_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#bucket_name DataDatabricksCleanRoomsCleanRooms#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#region DataDatabricksCleanRoomsCleanRooms#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#type DataDatabricksCleanRoomsCleanRooms#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e9164f2d251e3a857b13f61f3d47f6003abc05b9277767150dff2cbe902da26)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a732b11b61e755ab0b0acc76a45a26b3d72892235da8c3bc8a4087a7208f574)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abc3c68308e901812af9179f38eadd8c4c7cff88e0340b2df3932eaf5b1ce7c3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e40ffdfc8b9c1404774ebe287abdade211124fda01e43570c75cdeb6eb56016)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8615c84b617cf401bbdae3c739d1ae5bf81822ac6aa233d80d6a0b1c139d833)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fab58d012437a460f37f4b87f8fdef07f6ec1912a59e15889d4b9e171d54e250)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8669e50e7200b0348b9da10cd3f752d8e3cac0d3c4121fa67fb433c910a9c3e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__389dff9f7f7d3d6f0d0f74b2738c0ba018da7e2a2a08373ac5a9d3670bcc4cbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedPaths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureContainer")
    def azure_container(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureContainer"))

    @azure_container.setter
    def azure_container(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__798d3079332b1daebf00242a8344c20f79a3d3049d857511d1f256ea07dadd20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureContainer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureDnsZone")
    def azure_dns_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureDnsZone"))

    @azure_dns_zone.setter
    def azure_dns_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e50c201fce56563d24d4ff942c270354c628ea151cb4bbdee649986694e9f9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureDnsZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccount")
    def azure_storage_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageAccount"))

    @azure_storage_account.setter
    def azure_storage_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e692ff8e79488a4ab90d78ff82e69d2e57128e593f909c3b54f4d4e5a111f660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageService")
    def azure_storage_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageService"))

    @azure_storage_service.setter
    def azure_storage_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9af86f7b902eb0112ac236eef327a0739e590d0a03659d6d95c68c207bf7b9ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5073a531d5d7c40b040a997ab1afa36afb80c5056d31ae7368d51d3cf43a9f30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3e20cbf04e4305811338f575910d1347ef6881d31d9cd69055d5dbe1d9ce0cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__351b0af670381913aeec18dfc4d2e66896f6c2c41ceb247f7e0c0cafdfc85c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__735f36aa98cef7d69b18a5e9cb6676e76938121085580cdb266b19eae06d38f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode",
    jsii_struct_bases=[],
    name_mapping={"log_only_mode_type": "logOnlyModeType", "workloads": "workloads"},
)
class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode:
    def __init__(
        self,
        *,
        log_only_mode_type: typing.Optional[builtins.str] = None,
        workloads: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param log_only_mode_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode_type DataDatabricksCleanRoomsCleanRooms#log_only_mode_type}.
        :param workloads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workloads DataDatabricksCleanRoomsCleanRooms#workloads}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340d85f48bad33047848e1bf927b6c0da1c8c6e71a8b349998ffce360ddce931)
            check_type(argname="argument log_only_mode_type", value=log_only_mode_type, expected_type=type_hints["log_only_mode_type"])
            check_type(argname="argument workloads", value=workloads, expected_type=type_hints["workloads"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_only_mode_type is not None:
            self._values["log_only_mode_type"] = log_only_mode_type
        if workloads is not None:
            self._values["workloads"] = workloads

    @builtins.property
    def log_only_mode_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode_type DataDatabricksCleanRoomsCleanRooms#log_only_mode_type}.'''
        result = self._values.get("log_only_mode_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workloads(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workloads DataDatabricksCleanRoomsCleanRooms#workloads}.'''
        result = self._values.get("workloads")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c30fc3299a00e7876379fb8ea4243894afd80366ac434b249117ff3c31d80b24)
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
            type_hints = typing.get_type_hints(_typecheckingstub__991bba10670a57df3d79109b8f00186dec877571777f08231b696543f72ee757)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logOnlyModeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloads")
    def workloads(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "workloads"))

    @workloads.setter
    def workloads(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e87e9bc5de936e4e38a9824c90c298a7f849fb8f295b6bba2493dccfa9f15277)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d5066db9acbbc5b05c4ad5b0a270a6b36073c0b03b0807e8230525652be8c35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__913a11d25ede51d0f852660376761fc3cac51ba669d685e3b0058ef90327f613)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAllowedInternetDestinations")
    def put_allowed_internet_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cbda3deb4123dc2cf4bc0baa9a9d601e97228d6e38488f72e3ced0febbaf87c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedInternetDestinations", [value]))

    @jsii.member(jsii_name="putAllowedStorageDestinations")
    def put_allowed_storage_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__027f14186fb78083c19f9934b4d6f9b195d8f5bfbd598717357bb4b2f0c37b24)
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
        :param log_only_mode_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode_type DataDatabricksCleanRoomsCleanRooms#log_only_mode_type}.
        :param workloads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workloads DataDatabricksCleanRoomsCleanRooms#workloads}.
        '''
        value = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode(
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
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList, jsii.get(self, "allowedInternetDestinations"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinations")
    def allowed_storage_destinations(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList, jsii.get(self, "allowedStorageDestinations"))

    @builtins.property
    @jsii.member(jsii_name="logOnlyMode")
    def log_only_mode(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference, jsii.get(self, "logOnlyMode"))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinationsInput")
    def allowed_internet_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]], jsii.get(self, "allowedInternetDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinationsInput")
    def allowed_storage_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]], jsii.get(self, "allowedStorageDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="logOnlyModeInput")
    def log_only_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]], jsii.get(self, "logOnlyModeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__8492ce31c167fbda47e2518f30c3c2eea1018206edf47e9c3114e43998e63c62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00d1d7a927d099594de1829818fecb5e94ae3b7b18f86ea55135be6ae35e3c06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f213b0db926bccfa63458661210587a1b4496a33560c75c1fceb447bdc727cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInternetAccess")
    def put_internet_access(
        self,
        *,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        log_only_mode: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode, typing.Dict[builtins.str, typing.Any]]] = None,
        restriction_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_internet_destinations DataDatabricksCleanRoomsCleanRooms#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#allowed_storage_destinations DataDatabricksCleanRoomsCleanRooms#allowed_storage_destinations}.
        :param log_only_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#log_only_mode DataDatabricksCleanRoomsCleanRooms#log_only_mode}.
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#restriction_mode DataDatabricksCleanRoomsCleanRooms#restriction_mode}.
        '''
        value = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess(
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
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference, jsii.get(self, "internetAccess"))

    @builtins.property
    @jsii.member(jsii_name="internetAccessInput")
    def internet_access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]], jsii.get(self, "internetAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba6a6cd79c9400c762c7c5914d832cd970faaa9712d44d41094b0c9151cd289)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b3bd6e0fe103f3e944a9df3c4cda9d4799de34998bcfd10c6da70fac80f5bc2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCollaborators")
    def put_collaborators(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__389afb406272ae867df9317bbf7f248e4028e443386aad89d922b5416942c087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCollaborators", [value]))

    @jsii.member(jsii_name="putEgressNetworkPolicy")
    def put_egress_network_policy(
        self,
        *,
        internet_access: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param internet_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#internet_access DataDatabricksCleanRoomsCleanRooms#internet_access}.
        '''
        value = DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy(
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
    def collaborators(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsList:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsList, jsii.get(self, "collaborators"))

    @builtins.property
    @jsii.member(jsii_name="complianceSecurityProfile")
    def compliance_security_profile(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfileOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfileOutputReference, jsii.get(self, "complianceSecurityProfile"))

    @builtins.property
    @jsii.member(jsii_name="creator")
    def creator(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreatorOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreatorOutputReference, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="egressNetworkPolicy")
    def egress_network_policy(
        self,
    ) -> DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyOutputReference:
        return typing.cast(DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyOutputReference, jsii.get(self, "egressNetworkPolicy"))

    @builtins.property
    @jsii.member(jsii_name="cloudVendorInput")
    def cloud_vendor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudVendorInput"))

    @builtins.property
    @jsii.member(jsii_name="collaboratorsInput")
    def collaborators_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]], jsii.get(self, "collaboratorsInput"))

    @builtins.property
    @jsii.member(jsii_name="egressNetworkPolicyInput")
    def egress_network_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]], jsii.get(self, "egressNetworkPolicyInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3e1b11e948b95611db13dc2c96cdb1d208d34b8da260226665f468b3b356b6da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudVendor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eed11c95f7fe5f01e92e328a6f62831387ec3f3e3f764c7254041bc0e859a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c866ead5854de7df6f4937dd660022f9c62b62e5f09532b7150dd3fd8fcc92a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCleanRoomsCleanRooms.DataDatabricksCleanRoomsCleanRoomsConfig",
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
class DataDatabricksCleanRoomsCleanRoomsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workspace_id DataDatabricksCleanRoomsCleanRooms#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b2d5f45cb5958d73453024a4b2764d2aafaf5f8549efab84a7f0979e31ddd4a)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/clean_rooms_clean_rooms#workspace_id DataDatabricksCleanRoomsCleanRooms#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksCleanRoomsCleanRoomsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksCleanRoomsCleanRooms",
    "DataDatabricksCleanRoomsCleanRoomsCleanRooms",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsList",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalogOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsList",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaboratorsOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfileOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreatorOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsList",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinationsOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsList",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinationsOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyModeOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoOutputReference",
    "DataDatabricksCleanRoomsCleanRoomsConfig",
]

publication.publish()

def _typecheckingstub__a6f3aafd18900f7c44f08832226142021e04d995ccbd768cb00e02598e8d1146(
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

def _typecheckingstub__be5e23783e1852455e5b7eab3b81661415fca6212ff6bde7afd0d126f2ccfdc1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6616dfeaf723842d331be7439c69561653a2c94df6fd9671f7a1eeaf9159d02c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__478ceb53cd30b96107b7f82519eb12628c67388bccf11efa8a800c493db3b787(
    *,
    comment: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    remote_detailed_info: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c9418b58fb0a8962578e8449edc127542c28f838e135bc2bee101d42a3c6e0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54bda2c4299fa77751535902bf710df3ac853501a77cc07c4912836b4ab4673b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ab75df8db891a48d9be940babfc46a5cfb5518a7056becf83bc9fc43a0142a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd11eb5405787fae797f480af70c6d83033f157bbbc37264957066becd5665a5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19e93c1233d8193f35111c68f0ffa1d637523fe74863e724a9fef05f0148c674(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c9836042c1d2426e9172b0d03815f4bdf91ae10d72730216a35fec03c4a79e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRooms]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84bc7dd7eacb8b9c521d006fd1c5d6a00ce59516d3667c6b97e8848001ab0720(
    *,
    catalog_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39510785446f5680940d754b2d8ea69f1471bee503523c1b2c5b005cf5dce24b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16bd911a7ad76c3c5e2585c38e8dc7530d9e7e19f9e080f8f761f51100dd0a72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a7798574d79cdec8812ed314735d6e7b8f50e23846491c90a6ff1aec058f42(
    value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsOutputCatalog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a80a85ce78cc124c137524fdd053f3765bebef1a486d5fc3f16127f19c4b53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c8d2466d71978538da54df6b4ad16e6cd5fe033cb3b101175123db73dc34db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__487da3ddbd10c8002f4738dcfdb5ba167554e14b240176bbaf843327111efd51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a99d30e20f81fcff0863199f245cff471f0bbad6c87ae1d5a0564f7c4f9e994e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca272b8e72746c1844671673a2bb84bb951003b096958a2db2d9a769ca3d3b0(
    value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRooms],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20718e11a0b5a4d9651928599ef15f429677c932c89083206a015ce4f18a34e7(
    *,
    cloud_vendor: typing.Optional[builtins.str] = None,
    collaborators: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]]] = None,
    egress_network_policy: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3487afbe1327c29205b157decfc96d292804fcabfe2cd6401137d4bfb94b341e(
    *,
    collaborator_alias: builtins.str,
    global_metastore_id: typing.Optional[builtins.str] = None,
    invite_recipient_email: typing.Optional[builtins.str] = None,
    invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550d83b31fed3bc690c48164a479b1dfd6f984a8d61546275b2f5ebe411c0fff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d3785070b50aadf959192bacfbded564835845c6ce6d9f6fc38f315be63c0c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e5ea6662001874ab2c42a37f45ae9f1e352e27c085303a21862590bbfe280c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cea3b541a78286025fae20a4590a57c98684ebebfad5f3af0844f0bdd23d7b0b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893d195d8de65fedc65a82a7aecce2d4561f6826edc8af2eecfa0cc4fa6c6822(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a84992589354dd4c40f07b7d72f9cb7c6782eb4c1bcd603e1ad1c695a54a887(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf7dd8b35d12536f1695eb3bfb583c50a73f1db0910cdf91da24348faf114879(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f1af3ecd5ae5d6cc29fc824b341a0f4039afa3eb89779165aefce4d0a7de3b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da57eebe273b8f55ea4ffa1c2bae86c8d40854b0490f4cea53812f41167f0c32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0db32cc4ea5179fcffffdd1c10ae73982db6b6cc71cf5b2fc9125dfe8f4b1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e81e7a68205e85e99358d3c3f055d861b12d84027d1226704c4e80b3282e994(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef9d0cb3de1765a6aa9fbf6e0d2ee63a6fe6fb7549047a1b0b4a31914e4740d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36deb36896f5bba8ab33116d9e7798380bbbfb99f9efd58b4f710160fb96456e(
    *,
    compliance_standards: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863fe03f1b02653c44f0a96b2046cea7a3484e98d6bb64f55634ca66476c9bff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f54499724e246e58760d3d1a38bcff2714198882a7eb53c0690db4c769840b5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4f91ac00f049125d2d37f94b5643aecf5e6e84e043c28518cde1e79024fd671(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4035687518a2fa64cbefa496f76cb150ba676037c6c1cbb204b46e27cbeaaf10(
    value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoComplianceSecurityProfile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de194aea49c02e9fcc2c3df6a057d575b1042db1b2200bdee11a2bc88cfdb9ff(
    *,
    collaborator_alias: builtins.str,
    global_metastore_id: typing.Optional[builtins.str] = None,
    invite_recipient_email: typing.Optional[builtins.str] = None,
    invite_recipient_workspace_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__774a351e8282cb8c4ec31c299e96cddb0a039d9d8a9beb927064a8c1fa0d8cf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d62e65e356c0bf9528c5d99022ec825fe761bb943a1dab4ef0e029de32f0da0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf7759b4cbe297812b2b63479e729f09f3fd7489f916fceb9174ff5319d5de5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__336314cab889ce14d395dc4fe1b9d8eeec8a2769ed8005dbd1ffc3557d38e129(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__527fd489a67dad7b5b88fb1d8c6b467207180b967dab93d385e6b3faaa0c1801(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a801916a6c9b072da2522cdc079c9a7e595a50d37b6bf74d950c36f578580bb(
    value: typing.Optional[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCreator],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59b440184889ac954709ed22eff8a50ecf388c100ebade934aeb5fde0f5a8a65(
    *,
    internet_access: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0f8f323eed631878748713af16907f33712498950b2bfdda5eaedd036366ba2(
    *,
    allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    log_only_mode: typing.Optional[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode, typing.Dict[builtins.str, typing.Any]]] = None,
    restriction_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cfe5d88d97e4b957d872e72717f9996c112c6e4112adbb0a6d98bdd3685b273(
    *,
    destination: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a4f234b3906535b49b1439453432e597ce08e243a2108e41b67306df502d4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c77c2af1b1950e6b2975ca1d163553e690ca4133a4816e35d9488abd51cd22e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724e617a11f645ba9712273f1fbfb262765682f4c9ee62c5ada2117c896f9c7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9b1c6a83357ea448ed136312b33452098f9fa9c40bc1b4f80a472e86b123703(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d56cef0cac71be7842771a29b730ebbff3cfe75d5432820389553e1e7c7fddf6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac069716c5959e28c49f257210a4012b575c72a8301d3e97864f3d27ef21f856(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1c8556a53fc4798c7efcdaa9be64fadbb46213006b403b2e680248a5780791(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1120131196ce3d3b1552274dda2a080340fcd979d4f523d3f37a5ea53b219f60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a097cb271415331e8109d60084894354d431ff735a7d638b2eafa15fb6730708(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__662cce819dd309177fe167005854cbd3cad1fc3b34b8de88a0244f128905c0f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211b16a76c59b002d4d19de01810b6603c0d8be5699c6430e1f1113ae4b9017d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad21d3171097fd8894d3b57c397993517aeb213167b8001f22c3aa0924ee23fb(
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

def _typecheckingstub__2e9164f2d251e3a857b13f61f3d47f6003abc05b9277767150dff2cbe902da26(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a732b11b61e755ab0b0acc76a45a26b3d72892235da8c3bc8a4087a7208f574(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abc3c68308e901812af9179f38eadd8c4c7cff88e0340b2df3932eaf5b1ce7c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e40ffdfc8b9c1404774ebe287abdade211124fda01e43570c75cdeb6eb56016(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8615c84b617cf401bbdae3c739d1ae5bf81822ac6aa233d80d6a0b1c139d833(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab58d012437a460f37f4b87f8fdef07f6ec1912a59e15889d4b9e171d54e250(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8669e50e7200b0348b9da10cd3f752d8e3cac0d3c4121fa67fb433c910a9c3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__389dff9f7f7d3d6f0d0f74b2738c0ba018da7e2a2a08373ac5a9d3670bcc4cbb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__798d3079332b1daebf00242a8344c20f79a3d3049d857511d1f256ea07dadd20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e50c201fce56563d24d4ff942c270354c628ea151cb4bbdee649986694e9f9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e692ff8e79488a4ab90d78ff82e69d2e57128e593f909c3b54f4d4e5a111f660(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9af86f7b902eb0112ac236eef327a0739e590d0a03659d6d95c68c207bf7b9ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5073a531d5d7c40b040a997ab1afa36afb80c5056d31ae7368d51d3cf43a9f30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e20cbf04e4305811338f575910d1347ef6881d31d9cd69055d5dbe1d9ce0cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__351b0af670381913aeec18dfc4d2e66896f6c2c41ceb247f7e0c0cafdfc85c04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__735f36aa98cef7d69b18a5e9cb6676e76938121085580cdb266b19eae06d38f2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340d85f48bad33047848e1bf927b6c0da1c8c6e71a8b349998ffce360ddce931(
    *,
    log_only_mode_type: typing.Optional[builtins.str] = None,
    workloads: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c30fc3299a00e7876379fb8ea4243894afd80366ac434b249117ff3c31d80b24(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__991bba10670a57df3d79109b8f00186dec877571777f08231b696543f72ee757(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e87e9bc5de936e4e38a9824c90c298a7f849fb8f295b6bba2493dccfa9f15277(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d5066db9acbbc5b05c4ad5b0a270a6b36073c0b03b0807e8230525652be8c35(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessLogOnlyMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__913a11d25ede51d0f852660376761fc3cac51ba669d685e3b0058ef90327f613(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cbda3deb4123dc2cf4bc0baa9a9d601e97228d6e38488f72e3ced0febbaf87c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__027f14186fb78083c19f9934b4d6f9b195d8f5bfbd598717357bb4b2f0c37b24(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8492ce31c167fbda47e2518f30c3c2eea1018206edf47e9c3114e43998e63c62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d1d7a927d099594de1829818fecb5e94ae3b7b18f86ea55135be6ae35e3c06(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicyInternetAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f213b0db926bccfa63458661210587a1b4496a33560c75c1fceb447bdc727cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba6a6cd79c9400c762c7c5914d832cd970faaa9712d44d41094b0c9151cd289(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoEgressNetworkPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3bd6e0fe103f3e944a9df3c4cda9d4799de34998bcfd10c6da70fac80f5bc2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__389afb406272ae867df9317bbf7f248e4028e443386aad89d922b5416942c087(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfoCollaborators, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e1b11e948b95611db13dc2c96cdb1d208d34b8da260226665f468b3b356b6da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eed11c95f7fe5f01e92e328a6f62831387ec3f3e3f764c7254041bc0e859a15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c866ead5854de7df6f4937dd660022f9c62b62e5f09532b7150dd3fd8fcc92a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksCleanRoomsCleanRoomsCleanRoomsRemoteDetailedInfo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b2d5f45cb5958d73453024a4b2764d2aafaf5f8549efab84a7f0979e31ddd4a(
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
