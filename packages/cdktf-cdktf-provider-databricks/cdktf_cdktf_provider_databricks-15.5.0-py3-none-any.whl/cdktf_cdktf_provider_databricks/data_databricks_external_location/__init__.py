r'''
# `data_databricks_external_location`

Refer to the Terraform Registry for docs: [`data_databricks_external_location`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location).
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


class DataDatabricksExternalLocation(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocation",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location databricks_external_location}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        external_location_info: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location databricks_external_location} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.
        :param external_location_info: external_location_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#external_location_info DataDatabricksExternalLocation#external_location_info}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#id DataDatabricksExternalLocation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c59d9939c0b59a67d6c3776ccf010f86a1b8e47b61ed628cb143545179b96592)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksExternalLocationConfig(
            name=name,
            external_location_info=external_location_info,
            id=id,
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
        '''Generates CDKTF code for importing a DataDatabricksExternalLocation resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksExternalLocation to import.
        :param import_from_id: The id of the existing DataDatabricksExternalLocation that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksExternalLocation to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67d1c4655e14037d2854f4391cf80a7a3efb9af8e0424a2b94aca42f7312b382)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putExternalLocationInfo")
    def put_external_location_info(
        self,
        *,
        browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        comment: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        credential_id: typing.Optional[builtins.str] = None,
        credential_name: typing.Optional[builtins.str] = None,
        enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_details: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        file_event_queue: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueue", typing.Dict[builtins.str, typing.Any]]] = None,
        isolation_mode: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param browse_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#browse_only DataDatabricksExternalLocation#browse_only}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#comment DataDatabricksExternalLocation#comment}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_at DataDatabricksExternalLocation#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_by DataDatabricksExternalLocation#created_by}.
        :param credential_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_id DataDatabricksExternalLocation#credential_id}.
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_name DataDatabricksExternalLocation#credential_name}.
        :param enable_file_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#enable_file_events DataDatabricksExternalLocation#enable_file_events}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#encryption_details DataDatabricksExternalLocation#encryption_details}
        :param fallback: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#fallback DataDatabricksExternalLocation#fallback}.
        :param file_event_queue: file_event_queue block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#file_event_queue DataDatabricksExternalLocation#file_event_queue}
        :param isolation_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#isolation_mode DataDatabricksExternalLocation#isolation_mode}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#metastore_id DataDatabricksExternalLocation#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#owner DataDatabricksExternalLocation#owner}.
        :param read_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#read_only DataDatabricksExternalLocation#read_only}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_at DataDatabricksExternalLocation#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_by DataDatabricksExternalLocation#updated_by}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#url DataDatabricksExternalLocation#url}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfo(
            browse_only=browse_only,
            comment=comment,
            created_at=created_at,
            created_by=created_by,
            credential_id=credential_id,
            credential_name=credential_name,
            enable_file_events=enable_file_events,
            encryption_details=encryption_details,
            fallback=fallback,
            file_event_queue=file_event_queue,
            isolation_mode=isolation_mode,
            metastore_id=metastore_id,
            name=name,
            owner=owner,
            read_only=read_only,
            updated_at=updated_at,
            updated_by=updated_by,
            url=url,
        )

        return typing.cast(None, jsii.invoke(self, "putExternalLocationInfo", [value]))

    @jsii.member(jsii_name="resetExternalLocationInfo")
    def reset_external_location_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalLocationInfo", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="externalLocationInfo")
    def external_location_info(
        self,
    ) -> "DataDatabricksExternalLocationExternalLocationInfoOutputReference":
        return typing.cast("DataDatabricksExternalLocationExternalLocationInfoOutputReference", jsii.get(self, "externalLocationInfo"))

    @builtins.property
    @jsii.member(jsii_name="externalLocationInfoInput")
    def external_location_info_input(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfo"]:
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfo"], jsii.get(self, "externalLocationInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31435708a7ce055e2a8e20b2610ac180a0d0e098865d9a4f934945cdfd913b64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1727fb2aa34163e8b66bd4989ac2a2c0aa42a37bde2b223407e900220c8f57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationConfig",
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
        "external_location_info": "externalLocationInfo",
        "id": "id",
    },
)
class DataDatabricksExternalLocationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        external_location_info: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.
        :param external_location_info: external_location_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#external_location_info DataDatabricksExternalLocation#external_location_info}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#id DataDatabricksExternalLocation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(external_location_info, dict):
            external_location_info = DataDatabricksExternalLocationExternalLocationInfo(**external_location_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f31aac2ad6d10ab58e403e8f0fd2e61d63b07300aa024df37970c726694a137)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument external_location_info", value=external_location_info, expected_type=type_hints["external_location_info"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
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
        if external_location_info is not None:
            self._values["external_location_info"] = external_location_info
        if id is not None:
            self._values["id"] = id

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def external_location_info(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfo"]:
        '''external_location_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#external_location_info DataDatabricksExternalLocation#external_location_info}
        '''
        result = self._values.get("external_location_info")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfo"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#id DataDatabricksExternalLocation#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfo",
    jsii_struct_bases=[],
    name_mapping={
        "browse_only": "browseOnly",
        "comment": "comment",
        "created_at": "createdAt",
        "created_by": "createdBy",
        "credential_id": "credentialId",
        "credential_name": "credentialName",
        "enable_file_events": "enableFileEvents",
        "encryption_details": "encryptionDetails",
        "fallback": "fallback",
        "file_event_queue": "fileEventQueue",
        "isolation_mode": "isolationMode",
        "metastore_id": "metastoreId",
        "name": "name",
        "owner": "owner",
        "read_only": "readOnly",
        "updated_at": "updatedAt",
        "updated_by": "updatedBy",
        "url": "url",
    },
)
class DataDatabricksExternalLocationExternalLocationInfo:
    def __init__(
        self,
        *,
        browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        comment: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        credential_id: typing.Optional[builtins.str] = None,
        credential_name: typing.Optional[builtins.str] = None,
        enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_details: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        file_event_queue: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueue", typing.Dict[builtins.str, typing.Any]]] = None,
        isolation_mode: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param browse_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#browse_only DataDatabricksExternalLocation#browse_only}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#comment DataDatabricksExternalLocation#comment}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_at DataDatabricksExternalLocation#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_by DataDatabricksExternalLocation#created_by}.
        :param credential_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_id DataDatabricksExternalLocation#credential_id}.
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_name DataDatabricksExternalLocation#credential_name}.
        :param enable_file_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#enable_file_events DataDatabricksExternalLocation#enable_file_events}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#encryption_details DataDatabricksExternalLocation#encryption_details}
        :param fallback: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#fallback DataDatabricksExternalLocation#fallback}.
        :param file_event_queue: file_event_queue block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#file_event_queue DataDatabricksExternalLocation#file_event_queue}
        :param isolation_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#isolation_mode DataDatabricksExternalLocation#isolation_mode}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#metastore_id DataDatabricksExternalLocation#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#owner DataDatabricksExternalLocation#owner}.
        :param read_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#read_only DataDatabricksExternalLocation#read_only}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_at DataDatabricksExternalLocation#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_by DataDatabricksExternalLocation#updated_by}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#url DataDatabricksExternalLocation#url}.
        '''
        if isinstance(encryption_details, dict):
            encryption_details = DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails(**encryption_details)
        if isinstance(file_event_queue, dict):
            file_event_queue = DataDatabricksExternalLocationExternalLocationInfoFileEventQueue(**file_event_queue)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57eec9b93b819ed192cc53a7d8282b78d092b4171e07919232b818dfd9f18875)
            check_type(argname="argument browse_only", value=browse_only, expected_type=type_hints["browse_only"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument credential_id", value=credential_id, expected_type=type_hints["credential_id"])
            check_type(argname="argument credential_name", value=credential_name, expected_type=type_hints["credential_name"])
            check_type(argname="argument enable_file_events", value=enable_file_events, expected_type=type_hints["enable_file_events"])
            check_type(argname="argument encryption_details", value=encryption_details, expected_type=type_hints["encryption_details"])
            check_type(argname="argument fallback", value=fallback, expected_type=type_hints["fallback"])
            check_type(argname="argument file_event_queue", value=file_event_queue, expected_type=type_hints["file_event_queue"])
            check_type(argname="argument isolation_mode", value=isolation_mode, expected_type=type_hints["isolation_mode"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument read_only", value=read_only, expected_type=type_hints["read_only"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument updated_by", value=updated_by, expected_type=type_hints["updated_by"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if browse_only is not None:
            self._values["browse_only"] = browse_only
        if comment is not None:
            self._values["comment"] = comment
        if created_at is not None:
            self._values["created_at"] = created_at
        if created_by is not None:
            self._values["created_by"] = created_by
        if credential_id is not None:
            self._values["credential_id"] = credential_id
        if credential_name is not None:
            self._values["credential_name"] = credential_name
        if enable_file_events is not None:
            self._values["enable_file_events"] = enable_file_events
        if encryption_details is not None:
            self._values["encryption_details"] = encryption_details
        if fallback is not None:
            self._values["fallback"] = fallback
        if file_event_queue is not None:
            self._values["file_event_queue"] = file_event_queue
        if isolation_mode is not None:
            self._values["isolation_mode"] = isolation_mode
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if read_only is not None:
            self._values["read_only"] = read_only
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if updated_by is not None:
            self._values["updated_by"] = updated_by
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def browse_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#browse_only DataDatabricksExternalLocation#browse_only}.'''
        result = self._values.get("browse_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#comment DataDatabricksExternalLocation#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_at DataDatabricksExternalLocation#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#created_by DataDatabricksExternalLocation#created_by}.'''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credential_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_id DataDatabricksExternalLocation#credential_id}.'''
        result = self._values.get("credential_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credential_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#credential_name DataDatabricksExternalLocation#credential_name}.'''
        result = self._values.get("credential_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_file_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#enable_file_events DataDatabricksExternalLocation#enable_file_events}.'''
        result = self._values.get("enable_file_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_details(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails"]:
        '''encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#encryption_details DataDatabricksExternalLocation#encryption_details}
        '''
        result = self._values.get("encryption_details")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails"], result)

    @builtins.property
    def fallback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#fallback DataDatabricksExternalLocation#fallback}.'''
        result = self._values.get("fallback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def file_event_queue(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueue"]:
        '''file_event_queue block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#file_event_queue DataDatabricksExternalLocation#file_event_queue}
        '''
        result = self._values.get("file_event_queue")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueue"], result)

    @builtins.property
    def isolation_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#isolation_mode DataDatabricksExternalLocation#isolation_mode}.'''
        result = self._values.get("isolation_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#metastore_id DataDatabricksExternalLocation#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#name DataDatabricksExternalLocation#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#owner DataDatabricksExternalLocation#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#read_only DataDatabricksExternalLocation#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_at DataDatabricksExternalLocation#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def updated_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#updated_by DataDatabricksExternalLocation#updated_by}.'''
        result = self._values.get("updated_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#url DataDatabricksExternalLocation#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"sse_encryption_details": "sseEncryptionDetails"},
)
class DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails:
    def __init__(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#sse_encryption_details DataDatabricksExternalLocation#sse_encryption_details}
        '''
        if isinstance(sse_encryption_details, dict):
            sse_encryption_details = DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails(**sse_encryption_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5401e96048e30525204680ed98d569a21b1abc48fed3b75859d5814e12b74252)
            check_type(argname="argument sse_encryption_details", value=sse_encryption_details, expected_type=type_hints["sse_encryption_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sse_encryption_details is not None:
            self._values["sse_encryption_details"] = sse_encryption_details

    @builtins.property
    def sse_encryption_details(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails"]:
        '''sse_encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#sse_encryption_details DataDatabricksExternalLocation#sse_encryption_details}
        '''
        result = self._values.get("sse_encryption_details")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40f28ca0420538fbf4f0d87032bc2cb71273aff917b4afac7d05584b96f4f300)
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
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#algorithm DataDatabricksExternalLocation#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#aws_kms_key_arn DataDatabricksExternalLocation#aws_kms_key_arn}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails(
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
    ) -> "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetailsOutputReference":
        return typing.cast("DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetailsOutputReference", jsii.get(self, "sseEncryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="sseEncryptionDetailsInput")
    def sse_encryption_details_input(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails"]:
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails"], jsii.get(self, "sseEncryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__522a88f6a6478942ab2b156fbc29f4f1c61bab6077e421582aa65bbc7a3b9036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"algorithm": "algorithm", "aws_kms_key_arn": "awsKmsKeyArn"},
)
class DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails:
    def __init__(
        self,
        *,
        algorithm: typing.Optional[builtins.str] = None,
        aws_kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#algorithm DataDatabricksExternalLocation#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#aws_kms_key_arn DataDatabricksExternalLocation#aws_kms_key_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f72ae9c8c5d788aca13c8eef9030d4ca962614603e02c6b3b58d7c0721ded003)
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument aws_kms_key_arn", value=aws_kms_key_arn, expected_type=type_hints["aws_kms_key_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if aws_kms_key_arn is not None:
            self._values["aws_kms_key_arn"] = aws_kms_key_arn

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#algorithm DataDatabricksExternalLocation#algorithm}.'''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#aws_kms_key_arn DataDatabricksExternalLocation#aws_kms_key_arn}.'''
        result = self._values.get("aws_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96ee38452712ec521b340abdbe69d7c334df7ed77d576277fdf55c84b631b52b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__285903728bf7be4b6cf703c5229625d91d71439db5377f840af8d91777c784c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsKmsKeyArn")
    def aws_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsKmsKeyArn"))

    @aws_kms_key_arn.setter
    def aws_kms_key_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea078e49d080420a59a374c9c784068dd955f19a6b9a0cc7ffefc29c2821e2cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsKmsKeyArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e378d49e0b8d0d7ec68ec537a7743f083bdfd233cadd3ad1f46f9bd5c026dd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueue",
    jsii_struct_bases=[],
    name_mapping={
        "managed_aqs": "managedAqs",
        "managed_pubsub": "managedPubsub",
        "managed_sqs": "managedSqs",
        "provided_aqs": "providedAqs",
        "provided_pubsub": "providedPubsub",
        "provided_sqs": "providedSqs",
    },
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueue:
    def __init__(
        self,
        *,
        managed_aqs: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_pubsub: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_sqs: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_aqs: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_pubsub: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_sqs: typing.Optional[typing.Union["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param managed_aqs: managed_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_aqs DataDatabricksExternalLocation#managed_aqs}
        :param managed_pubsub: managed_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_pubsub DataDatabricksExternalLocation#managed_pubsub}
        :param managed_sqs: managed_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_sqs DataDatabricksExternalLocation#managed_sqs}
        :param provided_aqs: provided_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_aqs DataDatabricksExternalLocation#provided_aqs}
        :param provided_pubsub: provided_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_pubsub DataDatabricksExternalLocation#provided_pubsub}
        :param provided_sqs: provided_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_sqs DataDatabricksExternalLocation#provided_sqs}
        '''
        if isinstance(managed_aqs, dict):
            managed_aqs = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs(**managed_aqs)
        if isinstance(managed_pubsub, dict):
            managed_pubsub = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub(**managed_pubsub)
        if isinstance(managed_sqs, dict):
            managed_sqs = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs(**managed_sqs)
        if isinstance(provided_aqs, dict):
            provided_aqs = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs(**provided_aqs)
        if isinstance(provided_pubsub, dict):
            provided_pubsub = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub(**provided_pubsub)
        if isinstance(provided_sqs, dict):
            provided_sqs = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs(**provided_sqs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c68b316dededdae6fe7c81eaa03b4d49ff4f7c89389ef800b7cd02455b8f3040)
            check_type(argname="argument managed_aqs", value=managed_aqs, expected_type=type_hints["managed_aqs"])
            check_type(argname="argument managed_pubsub", value=managed_pubsub, expected_type=type_hints["managed_pubsub"])
            check_type(argname="argument managed_sqs", value=managed_sqs, expected_type=type_hints["managed_sqs"])
            check_type(argname="argument provided_aqs", value=provided_aqs, expected_type=type_hints["provided_aqs"])
            check_type(argname="argument provided_pubsub", value=provided_pubsub, expected_type=type_hints["provided_pubsub"])
            check_type(argname="argument provided_sqs", value=provided_sqs, expected_type=type_hints["provided_sqs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_aqs is not None:
            self._values["managed_aqs"] = managed_aqs
        if managed_pubsub is not None:
            self._values["managed_pubsub"] = managed_pubsub
        if managed_sqs is not None:
            self._values["managed_sqs"] = managed_sqs
        if provided_aqs is not None:
            self._values["provided_aqs"] = provided_aqs
        if provided_pubsub is not None:
            self._values["provided_pubsub"] = provided_pubsub
        if provided_sqs is not None:
            self._values["provided_sqs"] = provided_sqs

    @builtins.property
    def managed_aqs(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs"]:
        '''managed_aqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_aqs DataDatabricksExternalLocation#managed_aqs}
        '''
        result = self._values.get("managed_aqs")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs"], result)

    @builtins.property
    def managed_pubsub(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub"]:
        '''managed_pubsub block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_pubsub DataDatabricksExternalLocation#managed_pubsub}
        '''
        result = self._values.get("managed_pubsub")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub"], result)

    @builtins.property
    def managed_sqs(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs"]:
        '''managed_sqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_sqs DataDatabricksExternalLocation#managed_sqs}
        '''
        result = self._values.get("managed_sqs")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs"], result)

    @builtins.property
    def provided_aqs(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs"]:
        '''provided_aqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_aqs DataDatabricksExternalLocation#provided_aqs}
        '''
        result = self._values.get("provided_aqs")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs"], result)

    @builtins.property
    def provided_pubsub(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub"]:
        '''provided_pubsub block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_pubsub DataDatabricksExternalLocation#provided_pubsub}
        '''
        result = self._values.get("provided_pubsub")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub"], result)

    @builtins.property
    def provided_sqs(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs"]:
        '''provided_sqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_sqs DataDatabricksExternalLocation#provided_sqs}
        '''
        result = self._values.get("provided_sqs")
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs",
    jsii_struct_bases=[],
    name_mapping={
        "managed_resource_id": "managedResourceId",
        "queue_url": "queueUrl",
        "resource_group": "resourceGroup",
        "subscription_id": "subscriptionId",
    },
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2782f607103d9dbaeff1bffa0ff0dd788e5470eaea77ce581df548e5ced0ad3)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
            check_type(argname="argument resource_group", value=resource_group, expected_type=type_hints["resource_group"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if queue_url is not None:
            self._values["queue_url"] = queue_url
        if resource_group is not None:
            self._values["resource_group"] = resource_group
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.'''
        result = self._values.get("resource_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.'''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72b3e9e62c12730df274d17b6dfadc50d439678d177ea5ad729e0f510355f838)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @jsii.member(jsii_name="resetResourceGroup")
    def reset_resource_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroup", []))

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupInput")
    def resource_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__947455240db1df295d4487e0de402a62ce8a1cfe47f7c69bbbea8d68aab7255c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b257245238dfd5dded77a53dab2fe99b01bfaaddbaa2b8dd7f6caf7c6c0fa09d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroup")
    def resource_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroup"))

    @resource_group.setter
    def resource_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f864ee88ec7bb0d3057a0959f5cdc299c89ee7bb54eb66f84bb82c18eaa517f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d386e91b87b8bc53f93a49290501fc0fe514a95bdb8e56cddd3ec77d42cd20c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__421ff49a94303f9af7c621ec2a9e30cce1389d248867263e7b2fe237dbc0256c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub",
    jsii_struct_bases=[],
    name_mapping={
        "managed_resource_id": "managedResourceId",
        "subscription_name": "subscriptionName",
    },
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__254c12f209b5c27727c48cb7a0fffc18c00b01d6239b86086d12ad880c8a0acc)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument subscription_name", value=subscription_name, expected_type=type_hints["subscription_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if subscription_name is not None:
            self._values["subscription_name"] = subscription_name

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.'''
        result = self._values.get("subscription_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsubOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsubOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28ee12a32703dc588443e204c2479f930032b22d296096f3b22c7fc76d9c84b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetSubscriptionName")
    def reset_subscription_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionName", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionNameInput")
    def subscription_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e722db363fb5c06bec7abda8d812c2b4955ffd3bdb2ad3ef93948b44e99b99df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionName"))

    @subscription_name.setter
    def subscription_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff91b6326983a7df55db1f8e98bb8a30363a91504b4bc07699aa585b1b66f9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e5c83c844edd9e81bbb66977af8e8b9e12be4618d7bc1bc00ac200d4c4b9b7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs",
    jsii_struct_bases=[],
    name_mapping={"managed_resource_id": "managedResourceId", "queue_url": "queueUrl"},
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b42468b479a082c6ab6c8711671a10bf52e1efb663aff39ea96679335d514afb)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if queue_url is not None:
            self._values["queue_url"] = queue_url

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a273d5436ef5e11c423d9b4409434ed064215438656888a25ff25415dab903c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ee524ee9b20670e50c9dfb714bc02139e0d75824ae3eb5f604a62a62d048cc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44899a2708583946ebd19dc2b823538082193964dc9693ac10ab5eff7d09ce78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b956f048b34aad35cebd56346c5d1b0de940de0ac7fb26cbc9600cbde358a1de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e68f26f708464d55601d3c18fb536bc23f65b633e1083b3569fa97db6106f905)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putManagedAqs")
    def put_managed_aqs(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs(
            managed_resource_id=managed_resource_id,
            queue_url=queue_url,
            resource_group=resource_group,
            subscription_id=subscription_id,
        )

        return typing.cast(None, jsii.invoke(self, "putManagedAqs", [value]))

    @jsii.member(jsii_name="putManagedPubsub")
    def put_managed_pubsub(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub(
            managed_resource_id=managed_resource_id,
            subscription_name=subscription_name,
        )

        return typing.cast(None, jsii.invoke(self, "putManagedPubsub", [value]))

    @jsii.member(jsii_name="putManagedSqs")
    def put_managed_sqs(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs(
            managed_resource_id=managed_resource_id, queue_url=queue_url
        )

        return typing.cast(None, jsii.invoke(self, "putManagedSqs", [value]))

    @jsii.member(jsii_name="putProvidedAqs")
    def put_provided_aqs(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs(
            managed_resource_id=managed_resource_id,
            queue_url=queue_url,
            resource_group=resource_group,
            subscription_id=subscription_id,
        )

        return typing.cast(None, jsii.invoke(self, "putProvidedAqs", [value]))

    @jsii.member(jsii_name="putProvidedPubsub")
    def put_provided_pubsub(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub(
            managed_resource_id=managed_resource_id,
            subscription_name=subscription_name,
        )

        return typing.cast(None, jsii.invoke(self, "putProvidedPubsub", [value]))

    @jsii.member(jsii_name="putProvidedSqs")
    def put_provided_sqs(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs(
            managed_resource_id=managed_resource_id, queue_url=queue_url
        )

        return typing.cast(None, jsii.invoke(self, "putProvidedSqs", [value]))

    @jsii.member(jsii_name="resetManagedAqs")
    def reset_managed_aqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedAqs", []))

    @jsii.member(jsii_name="resetManagedPubsub")
    def reset_managed_pubsub(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedPubsub", []))

    @jsii.member(jsii_name="resetManagedSqs")
    def reset_managed_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedSqs", []))

    @jsii.member(jsii_name="resetProvidedAqs")
    def reset_provided_aqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedAqs", []))

    @jsii.member(jsii_name="resetProvidedPubsub")
    def reset_provided_pubsub(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedPubsub", []))

    @jsii.member(jsii_name="resetProvidedSqs")
    def reset_provided_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedSqs", []))

    @builtins.property
    @jsii.member(jsii_name="managedAqs")
    def managed_aqs(
        self,
    ) -> DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqsOutputReference:
        return typing.cast(DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqsOutputReference, jsii.get(self, "managedAqs"))

    @builtins.property
    @jsii.member(jsii_name="managedPubsub")
    def managed_pubsub(
        self,
    ) -> DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsubOutputReference:
        return typing.cast(DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsubOutputReference, jsii.get(self, "managedPubsub"))

    @builtins.property
    @jsii.member(jsii_name="managedSqs")
    def managed_sqs(
        self,
    ) -> DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqsOutputReference:
        return typing.cast(DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqsOutputReference, jsii.get(self, "managedSqs"))

    @builtins.property
    @jsii.member(jsii_name="providedAqs")
    def provided_aqs(
        self,
    ) -> "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqsOutputReference":
        return typing.cast("DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqsOutputReference", jsii.get(self, "providedAqs"))

    @builtins.property
    @jsii.member(jsii_name="providedPubsub")
    def provided_pubsub(
        self,
    ) -> "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsubOutputReference":
        return typing.cast("DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsubOutputReference", jsii.get(self, "providedPubsub"))

    @builtins.property
    @jsii.member(jsii_name="providedSqs")
    def provided_sqs(
        self,
    ) -> "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqsOutputReference":
        return typing.cast("DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqsOutputReference", jsii.get(self, "providedSqs"))

    @builtins.property
    @jsii.member(jsii_name="managedAqsInput")
    def managed_aqs_input(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs], jsii.get(self, "managedAqsInput"))

    @builtins.property
    @jsii.member(jsii_name="managedPubsubInput")
    def managed_pubsub_input(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub], jsii.get(self, "managedPubsubInput"))

    @builtins.property
    @jsii.member(jsii_name="managedSqsInput")
    def managed_sqs_input(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs], jsii.get(self, "managedSqsInput"))

    @builtins.property
    @jsii.member(jsii_name="providedAqsInput")
    def provided_aqs_input(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs"]:
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs"], jsii.get(self, "providedAqsInput"))

    @builtins.property
    @jsii.member(jsii_name="providedPubsubInput")
    def provided_pubsub_input(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub"]:
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub"], jsii.get(self, "providedPubsubInput"))

    @builtins.property
    @jsii.member(jsii_name="providedSqsInput")
    def provided_sqs_input(
        self,
    ) -> typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs"]:
        return typing.cast(typing.Optional["DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs"], jsii.get(self, "providedSqsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e3c9a870f73e40ab076166969fe73769e964f8ce218c8f91482b95e5d022ce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs",
    jsii_struct_bases=[],
    name_mapping={
        "managed_resource_id": "managedResourceId",
        "queue_url": "queueUrl",
        "resource_group": "resourceGroup",
        "subscription_id": "subscriptionId",
    },
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b48eed3a27e561fb3a1cd3b8540aefd6678de6f9dfcf4068f9e177c929bf072b)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
            check_type(argname="argument resource_group", value=resource_group, expected_type=type_hints["resource_group"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if queue_url is not None:
            self._values["queue_url"] = queue_url
        if resource_group is not None:
            self._values["resource_group"] = resource_group
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#resource_group DataDatabricksExternalLocation#resource_group}.'''
        result = self._values.get("resource_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_id DataDatabricksExternalLocation#subscription_id}.'''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a895867bb5e135a707536b6667eaab780d2d17238712eed8c0750a90732f287)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @jsii.member(jsii_name="resetResourceGroup")
    def reset_resource_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroup", []))

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupInput")
    def resource_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f1bcf7b83868f0fd4d82671c9ebdd4bcdb87509e8b0e6d23f1bbe2392be43ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5a3a20a2c83ec2655e23bbfa480e94d87660f9001210686668984e8e2ee817d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroup")
    def resource_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroup"))

    @resource_group.setter
    def resource_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c48c00ee42d086477ee2ac71ffef3eb5c1a28442ee7bd067e3de3c2ce64a1790)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb42b38326d48f9bba81f13450846f38cae89a8ab0f746ca7efc85bfe8a8bc94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c60f95a74e1450bd1413084743086f066e754808a252292001a46262cff7d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub",
    jsii_struct_bases=[],
    name_mapping={
        "managed_resource_id": "managedResourceId",
        "subscription_name": "subscriptionName",
    },
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bab68a47defc7c7cc127151651f96e891a296865928b2eea3a9c2e63186ab73)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument subscription_name", value=subscription_name, expected_type=type_hints["subscription_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if subscription_name is not None:
            self._values["subscription_name"] = subscription_name

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#subscription_name DataDatabricksExternalLocation#subscription_name}.'''
        result = self._values.get("subscription_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsubOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsubOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee0dbb8b9622195e5670e4dd63f258380e74f0f21344fe49136185c4c866d869)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetSubscriptionName")
    def reset_subscription_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionName", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionNameInput")
    def subscription_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1e11b879bea2c1ff3c09023669caca81112984980232a079787ac4c8497d899)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionName"))

    @subscription_name.setter
    def subscription_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0e09cf9b141d190f6cabd9f33cbc3969964c9baff74e45903fe152a3dc80b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f1d8745fff6fba7c17fd4282e417571f3394771db7b34f1f8241b94f9a386d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs",
    jsii_struct_bases=[],
    name_mapping={"managed_resource_id": "managedResourceId", "queue_url": "queueUrl"},
)
class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs:
    def __init__(
        self,
        *,
        managed_resource_id: typing.Optional[builtins.str] = None,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69e373d0b73ae004233fed2b41b727a30ddd490fbc26fd7729e6f20a62e17c54)
            check_type(argname="argument managed_resource_id", value=managed_resource_id, expected_type=type_hints["managed_resource_id"])
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_resource_id is not None:
            self._values["managed_resource_id"] = managed_resource_id
        if queue_url is not None:
            self._values["queue_url"] = queue_url

    @builtins.property
    def managed_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_resource_id DataDatabricksExternalLocation#managed_resource_id}.'''
        result = self._values.get("managed_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#queue_url DataDatabricksExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4476a1bf12806a0f6b110903924d84866ade831f3c3d4a74bb95fc549330c678)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManagedResourceId")
    def reset_managed_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedResourceId", []))

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceIdInput")
    def managed_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @managed_resource_id.setter
    def managed_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80728b76fe4df3122795e05a345f719fe661367e8e42704a358ff64db5e92340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ff54d9d7b84905c19ef95df829de16efdc4c9f778a9ac8cf19298f79ae3a110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__594f85ae57202995419837c528b77bf3f16aeaa789956cba9fca26cab988ac9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksExternalLocationExternalLocationInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksExternalLocation.DataDatabricksExternalLocationExternalLocationInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f60de10b661f58977402d323e2a8d7c5422c2d422b450e60b16a3caf49c4581)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEncryptionDetails")
    def put_encryption_details(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#sse_encryption_details DataDatabricksExternalLocation#sse_encryption_details}
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails(
            sse_encryption_details=sse_encryption_details
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionDetails", [value]))

    @jsii.member(jsii_name="putFileEventQueue")
    def put_file_event_queue(
        self,
        *,
        managed_aqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
        managed_pubsub: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
        managed_sqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
        provided_aqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
        provided_pubsub: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
        provided_sqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param managed_aqs: managed_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_aqs DataDatabricksExternalLocation#managed_aqs}
        :param managed_pubsub: managed_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_pubsub DataDatabricksExternalLocation#managed_pubsub}
        :param managed_sqs: managed_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#managed_sqs DataDatabricksExternalLocation#managed_sqs}
        :param provided_aqs: provided_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_aqs DataDatabricksExternalLocation#provided_aqs}
        :param provided_pubsub: provided_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_pubsub DataDatabricksExternalLocation#provided_pubsub}
        :param provided_sqs: provided_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/external_location#provided_sqs DataDatabricksExternalLocation#provided_sqs}
        '''
        value = DataDatabricksExternalLocationExternalLocationInfoFileEventQueue(
            managed_aqs=managed_aqs,
            managed_pubsub=managed_pubsub,
            managed_sqs=managed_sqs,
            provided_aqs=provided_aqs,
            provided_pubsub=provided_pubsub,
            provided_sqs=provided_sqs,
        )

        return typing.cast(None, jsii.invoke(self, "putFileEventQueue", [value]))

    @jsii.member(jsii_name="resetBrowseOnly")
    def reset_browse_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrowseOnly", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetCredentialId")
    def reset_credential_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialId", []))

    @jsii.member(jsii_name="resetCredentialName")
    def reset_credential_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialName", []))

    @jsii.member(jsii_name="resetEnableFileEvents")
    def reset_enable_file_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableFileEvents", []))

    @jsii.member(jsii_name="resetEncryptionDetails")
    def reset_encryption_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionDetails", []))

    @jsii.member(jsii_name="resetFallback")
    def reset_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallback", []))

    @jsii.member(jsii_name="resetFileEventQueue")
    def reset_file_event_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileEventQueue", []))

    @jsii.member(jsii_name="resetIsolationMode")
    def reset_isolation_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsolationMode", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUpdatedBy")
    def reset_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBy", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetails")
    def encryption_details(
        self,
    ) -> DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsOutputReference:
        return typing.cast(DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsOutputReference, jsii.get(self, "encryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="fileEventQueue")
    def file_event_queue(
        self,
    ) -> DataDatabricksExternalLocationExternalLocationInfoFileEventQueueOutputReference:
        return typing.cast(DataDatabricksExternalLocationExternalLocationInfoFileEventQueueOutputReference, jsii.get(self, "fileEventQueue"))

    @builtins.property
    @jsii.member(jsii_name="browseOnlyInput")
    def browse_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "browseOnlyInput"))

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
    @jsii.member(jsii_name="credentialIdInput")
    def credential_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialIdInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialNameInput")
    def credential_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enableFileEventsInput")
    def enable_file_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableFileEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetailsInput")
    def encryption_details_input(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails], jsii.get(self, "encryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackInput")
    def fallback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="fileEventQueueInput")
    def file_event_queue_input(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue], jsii.get(self, "fileEventQueueInput"))

    @builtins.property
    @jsii.member(jsii_name="isolationModeInput")
    def isolation_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "isolationModeInput"))

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
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedByInput")
    def updated_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b446d5bc6e10ff6891683358698cb1584b2d3453380896d03a322786f340e56a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browseOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efce29ffde24913ee2b62812b46a226e7958a3fba0969f5cd284581f6b5eaa22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca76392996b99a65b710d7f20031e2cacc0975ae066cb7279a434f59dc25b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__087a81de464f1b45ee34ef702f6c42cac708cf3b48550413ba37663261a3537a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="credentialId")
    def credential_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialId"))

    @credential_id.setter
    def credential_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6812c28951fa758be5f10e2926066ee9f43f2020c2afe9d6686f98214265bf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="credentialName")
    def credential_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialName"))

    @credential_name.setter
    def credential_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eebfdccca6a43ee7751e531130db8ee1235cff7af206628a59cacfeb7344b728)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableFileEvents")
    def enable_file_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableFileEvents"))

    @enable_file_events.setter
    def enable_file_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee486672ffab85f13b37c328a63e938c48e415c80b8b1538a43e013103e4dfc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableFileEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallback")
    def fallback(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "fallback"))

    @fallback.setter
    def fallback(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a7181ba6b2dc63f644e758e9eca60159a28a38f013fa0a16268053a07cd425)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isolationMode")
    def isolation_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "isolationMode"))

    @isolation_mode.setter
    def isolation_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__659a61a39c6ed2fd98fc2be1ea413c583464f2da231205c9f466fe4e1a1eb965)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isolationMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e6a44e779585b60fa638e240bb3f31f4aac9c395eb941d8cd79a8d4dec33cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28ea76f0e2c1b244e762e77f25ccd0e5917cbed0d6edd1bd0833d391c66873af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3805e7e7d028d607dd0efe6bad6640e25eba70536017ea0f6a2478059f898772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87cc0df3a293bdcd6836fe4c0bafc730b799bca81b02c96679fa682af096edad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b746c84cb4337ba9ee7d0af4e23464e7130db25ec559d852f346a2f449ce8e78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @updated_by.setter
    def updated_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c0a1b9f83ff055df36f2a4336086e153b4b7bd8093861dcdc0c175d0b8c5f72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bb67f7fa845f28964197232ac7ce6e6d36e04b51e26a21d4fc80a940ef7da49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksExternalLocationExternalLocationInfo]:
        return typing.cast(typing.Optional[DataDatabricksExternalLocationExternalLocationInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c83f868cf30eaefeb908ca0673b7646085cb8c47d5aa9ae4e41128d1b52e790b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksExternalLocation",
    "DataDatabricksExternalLocationConfig",
    "DataDatabricksExternalLocationExternalLocationInfo",
    "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails",
    "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails",
    "DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetailsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueue",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsubOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsubOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs",
    "DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqsOutputReference",
    "DataDatabricksExternalLocationExternalLocationInfoOutputReference",
]

publication.publish()

def _typecheckingstub__c59d9939c0b59a67d6c3776ccf010f86a1b8e47b61ed628cb143545179b96592(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    external_location_info: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__67d1c4655e14037d2854f4391cf80a7a3efb9af8e0424a2b94aca42f7312b382(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31435708a7ce055e2a8e20b2610ac180a0d0e098865d9a4f934945cdfd913b64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1727fb2aa34163e8b66bd4989ac2a2c0aa42a37bde2b223407e900220c8f57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f31aac2ad6d10ab58e403e8f0fd2e61d63b07300aa024df37970c726694a137(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    external_location_info: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57eec9b93b819ed192cc53a7d8282b78d092b4171e07919232b818dfd9f18875(
    *,
    browse_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    comment: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[jsii.Number] = None,
    created_by: typing.Optional[builtins.str] = None,
    credential_id: typing.Optional[builtins.str] = None,
    credential_name: typing.Optional[builtins.str] = None,
    enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_details: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    file_event_queue: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue, typing.Dict[builtins.str, typing.Any]]] = None,
    isolation_mode: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    updated_at: typing.Optional[jsii.Number] = None,
    updated_by: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5401e96048e30525204680ed98d569a21b1abc48fed3b75859d5814e12b74252(
    *,
    sse_encryption_details: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40f28ca0420538fbf4f0d87032bc2cb71273aff917b4afac7d05584b96f4f300(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__522a88f6a6478942ab2b156fbc29f4f1c61bab6077e421582aa65bbc7a3b9036(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f72ae9c8c5d788aca13c8eef9030d4ca962614603e02c6b3b58d7c0721ded003(
    *,
    algorithm: typing.Optional[builtins.str] = None,
    aws_kms_key_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ee38452712ec521b340abdbe69d7c334df7ed77d576277fdf55c84b631b52b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__285903728bf7be4b6cf703c5229625d91d71439db5377f840af8d91777c784c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea078e49d080420a59a374c9c784068dd955f19a6b9a0cc7ffefc29c2821e2cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e378d49e0b8d0d7ec68ec537a7743f083bdfd233cadd3ad1f46f9bd5c026dd4(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoEncryptionDetailsSseEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c68b316dededdae6fe7c81eaa03b4d49ff4f7c89389ef800b7cd02455b8f3040(
    *,
    managed_aqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_pubsub: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_sqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_aqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_pubsub: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_sqs: typing.Optional[typing.Union[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2782f607103d9dbaeff1bffa0ff0dd788e5470eaea77ce581df548e5ced0ad3(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    queue_url: typing.Optional[builtins.str] = None,
    resource_group: typing.Optional[builtins.str] = None,
    subscription_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72b3e9e62c12730df274d17b6dfadc50d439678d177ea5ad729e0f510355f838(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__947455240db1df295d4487e0de402a62ce8a1cfe47f7c69bbbea8d68aab7255c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b257245238dfd5dded77a53dab2fe99b01bfaaddbaa2b8dd7f6caf7c6c0fa09d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f864ee88ec7bb0d3057a0959f5cdc299c89ee7bb54eb66f84bb82c18eaa517f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d386e91b87b8bc53f93a49290501fc0fe514a95bdb8e56cddd3ec77d42cd20c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__421ff49a94303f9af7c621ec2a9e30cce1389d248867263e7b2fe237dbc0256c(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedAqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254c12f209b5c27727c48cb7a0fffc18c00b01d6239b86086d12ad880c8a0acc(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    subscription_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ee12a32703dc588443e204c2479f930032b22d296096f3b22c7fc76d9c84b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e722db363fb5c06bec7abda8d812c2b4955ffd3bdb2ad3ef93948b44e99b99df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff91b6326983a7df55db1f8e98bb8a30363a91504b4bc07699aa585b1b66f9cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e5c83c844edd9e81bbb66977af8e8b9e12be4618d7bc1bc00ac200d4c4b9b7a(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedPubsub],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b42468b479a082c6ab6c8711671a10bf52e1efb663aff39ea96679335d514afb(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    queue_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a273d5436ef5e11c423d9b4409434ed064215438656888a25ff25415dab903c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ee524ee9b20670e50c9dfb714bc02139e0d75824ae3eb5f604a62a62d048cc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44899a2708583946ebd19dc2b823538082193964dc9693ac10ab5eff7d09ce78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b956f048b34aad35cebd56346c5d1b0de940de0ac7fb26cbc9600cbde358a1de(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueManagedSqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68f26f708464d55601d3c18fb536bc23f65b633e1083b3569fa97db6106f905(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e3c9a870f73e40ab076166969fe73769e964f8ce218c8f91482b95e5d022ce3(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b48eed3a27e561fb3a1cd3b8540aefd6678de6f9dfcf4068f9e177c929bf072b(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    queue_url: typing.Optional[builtins.str] = None,
    resource_group: typing.Optional[builtins.str] = None,
    subscription_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a895867bb5e135a707536b6667eaab780d2d17238712eed8c0750a90732f287(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f1bcf7b83868f0fd4d82671c9ebdd4bcdb87509e8b0e6d23f1bbe2392be43ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5a3a20a2c83ec2655e23bbfa480e94d87660f9001210686668984e8e2ee817d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c48c00ee42d086477ee2ac71ffef3eb5c1a28442ee7bd067e3de3c2ce64a1790(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb42b38326d48f9bba81f13450846f38cae89a8ab0f746ca7efc85bfe8a8bc94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c60f95a74e1450bd1413084743086f066e754808a252292001a46262cff7d80(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedAqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bab68a47defc7c7cc127151651f96e891a296865928b2eea3a9c2e63186ab73(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    subscription_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee0dbb8b9622195e5670e4dd63f258380e74f0f21344fe49136185c4c866d869(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1e11b879bea2c1ff3c09023669caca81112984980232a079787ac4c8497d899(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0e09cf9b141d190f6cabd9f33cbc3969964c9baff74e45903fe152a3dc80b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f1d8745fff6fba7c17fd4282e417571f3394771db7b34f1f8241b94f9a386d(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedPubsub],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e373d0b73ae004233fed2b41b727a30ddd490fbc26fd7729e6f20a62e17c54(
    *,
    managed_resource_id: typing.Optional[builtins.str] = None,
    queue_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4476a1bf12806a0f6b110903924d84866ade831f3c3d4a74bb95fc549330c678(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80728b76fe4df3122795e05a345f719fe661367e8e42704a358ff64db5e92340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ff54d9d7b84905c19ef95df829de16efdc4c9f778a9ac8cf19298f79ae3a110(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__594f85ae57202995419837c528b77bf3f16aeaa789956cba9fca26cab988ac9c(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfoFileEventQueueProvidedSqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f60de10b661f58977402d323e2a8d7c5422c2d422b450e60b16a3caf49c4581(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b446d5bc6e10ff6891683358698cb1584b2d3453380896d03a322786f340e56a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efce29ffde24913ee2b62812b46a226e7958a3fba0969f5cd284581f6b5eaa22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca76392996b99a65b710d7f20031e2cacc0975ae066cb7279a434f59dc25b91(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__087a81de464f1b45ee34ef702f6c42cac708cf3b48550413ba37663261a3537a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6812c28951fa758be5f10e2926066ee9f43f2020c2afe9d6686f98214265bf9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eebfdccca6a43ee7751e531130db8ee1235cff7af206628a59cacfeb7344b728(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee486672ffab85f13b37c328a63e938c48e415c80b8b1538a43e013103e4dfc7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a7181ba6b2dc63f644e758e9eca60159a28a38f013fa0a16268053a07cd425(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__659a61a39c6ed2fd98fc2be1ea413c583464f2da231205c9f466fe4e1a1eb965(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e6a44e779585b60fa638e240bb3f31f4aac9c395eb941d8cd79a8d4dec33cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ea76f0e2c1b244e762e77f25ccd0e5917cbed0d6edd1bd0833d391c66873af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3805e7e7d028d607dd0efe6bad6640e25eba70536017ea0f6a2478059f898772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87cc0df3a293bdcd6836fe4c0bafc730b799bca81b02c96679fa682af096edad(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b746c84cb4337ba9ee7d0af4e23464e7130db25ec559d852f346a2f449ce8e78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c0a1b9f83ff055df36f2a4336086e153b4b7bd8093861dcdc0c175d0b8c5f72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bb67f7fa845f28964197232ac7ce6e6d36e04b51e26a21d4fc80a940ef7da49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c83f868cf30eaefeb908ca0673b7646085cb8c47d5aa9ae4e41128d1b52e790b(
    value: typing.Optional[DataDatabricksExternalLocationExternalLocationInfo],
) -> None:
    """Type checking stubs"""
    pass
