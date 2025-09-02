r'''
# `data_databricks_metastore`

Refer to the Terraform Registry for docs: [`data_databricks_metastore`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore).
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


class DataDatabricksMetastore(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMetastore.DataDatabricksMetastore",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore databricks_metastore}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        metastore_info: typing.Optional[typing.Union["DataDatabricksMetastoreMetastoreInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore databricks_metastore} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#id DataDatabricksMetastore#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.
        :param metastore_info: metastore_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_info DataDatabricksMetastore#metastore_info}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92f4e4aba9b4143f5025d323ce738296d0534f71617907c1dadb4e8ee1a00f7f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksMetastoreConfig(
            id=id,
            metastore_id=metastore_id,
            metastore_info=metastore_info,
            name=name,
            region=region,
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
        '''Generates CDKTF code for importing a DataDatabricksMetastore resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksMetastore to import.
        :param import_from_id: The id of the existing DataDatabricksMetastore that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksMetastore to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c898dd205251d0f3e6801fe779c9c81b1cda37e04bdaafb3b30a333def38807)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putMetastoreInfo")
    def put_metastore_info(
        self,
        *,
        cloud: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        default_data_access_config_id: typing.Optional[builtins.str] = None,
        delta_sharing_organization_name: typing.Optional[builtins.str] = None,
        delta_sharing_recipient_token_lifetime_in_seconds: typing.Optional[jsii.Number] = None,
        delta_sharing_scope: typing.Optional[builtins.str] = None,
        external_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        global_metastore_id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        privilege_model_version: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        storage_root: typing.Optional[builtins.str] = None,
        storage_root_credential_id: typing.Optional[builtins.str] = None,
        storage_root_credential_name: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#cloud DataDatabricksMetastore#cloud}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_at DataDatabricksMetastore#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_by DataDatabricksMetastore#created_by}.
        :param default_data_access_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#default_data_access_config_id DataDatabricksMetastore#default_data_access_config_id}.
        :param delta_sharing_organization_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_organization_name DataDatabricksMetastore#delta_sharing_organization_name}.
        :param delta_sharing_recipient_token_lifetime_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_recipient_token_lifetime_in_seconds DataDatabricksMetastore#delta_sharing_recipient_token_lifetime_in_seconds}.
        :param delta_sharing_scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_scope DataDatabricksMetastore#delta_sharing_scope}.
        :param external_access_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#external_access_enabled DataDatabricksMetastore#external_access_enabled}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#global_metastore_id DataDatabricksMetastore#global_metastore_id}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#owner DataDatabricksMetastore#owner}.
        :param privilege_model_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#privilege_model_version DataDatabricksMetastore#privilege_model_version}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.
        :param storage_root: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root DataDatabricksMetastore#storage_root}.
        :param storage_root_credential_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_id DataDatabricksMetastore#storage_root_credential_id}.
        :param storage_root_credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_name DataDatabricksMetastore#storage_root_credential_name}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_at DataDatabricksMetastore#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_by DataDatabricksMetastore#updated_by}.
        '''
        value = DataDatabricksMetastoreMetastoreInfo(
            cloud=cloud,
            created_at=created_at,
            created_by=created_by,
            default_data_access_config_id=default_data_access_config_id,
            delta_sharing_organization_name=delta_sharing_organization_name,
            delta_sharing_recipient_token_lifetime_in_seconds=delta_sharing_recipient_token_lifetime_in_seconds,
            delta_sharing_scope=delta_sharing_scope,
            external_access_enabled=external_access_enabled,
            global_metastore_id=global_metastore_id,
            metastore_id=metastore_id,
            name=name,
            owner=owner,
            privilege_model_version=privilege_model_version,
            region=region,
            storage_root=storage_root,
            storage_root_credential_id=storage_root_credential_id,
            storage_root_credential_name=storage_root_credential_name,
            updated_at=updated_at,
            updated_by=updated_by,
        )

        return typing.cast(None, jsii.invoke(self, "putMetastoreInfo", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetMetastoreInfo")
    def reset_metastore_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreInfo", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

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
    @jsii.member(jsii_name="metastoreInfo")
    def metastore_info(self) -> "DataDatabricksMetastoreMetastoreInfoOutputReference":
        return typing.cast("DataDatabricksMetastoreMetastoreInfoOutputReference", jsii.get(self, "metastoreInfo"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreIdInput")
    def metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreInfoInput")
    def metastore_info_input(
        self,
    ) -> typing.Optional["DataDatabricksMetastoreMetastoreInfo"]:
        return typing.cast(typing.Optional["DataDatabricksMetastoreMetastoreInfo"], jsii.get(self, "metastoreInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdaea571b668c1c24b3a2c57a8ee15eabb7dc77892e9a12ecd4cf396d66d297e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2205a4c1d156165653d158f61d41b6818ce254924eb0aaf5684371fac3626f99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a1551961ce0ffd5a26b5b23c91a047fa6d2b0696eaacff63247397011cfa34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5c818aae874b06d1e2a767b7e884694a1cf172be6c37731671d28e4604d8197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMetastore.DataDatabricksMetastoreConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "metastore_id": "metastoreId",
        "metastore_info": "metastoreInfo",
        "name": "name",
        "region": "region",
    },
)
class DataDatabricksMetastoreConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        metastore_info: typing.Optional[typing.Union["DataDatabricksMetastoreMetastoreInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#id DataDatabricksMetastore#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.
        :param metastore_info: metastore_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_info DataDatabricksMetastore#metastore_info}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(metastore_info, dict):
            metastore_info = DataDatabricksMetastoreMetastoreInfo(**metastore_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14a89737b9b2fb44a530b283d85293e8619188e79e4ccdb6b035351e3d7425b9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument metastore_info", value=metastore_info, expected_type=type_hints["metastore_info"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
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
        if id is not None:
            self._values["id"] = id
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if metastore_info is not None:
            self._values["metastore_info"] = metastore_info
        if name is not None:
            self._values["name"] = name
        if region is not None:
            self._values["region"] = region

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#id DataDatabricksMetastore#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_info(self) -> typing.Optional["DataDatabricksMetastoreMetastoreInfo"]:
        '''metastore_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_info DataDatabricksMetastore#metastore_info}
        '''
        result = self._values.get("metastore_info")
        return typing.cast(typing.Optional["DataDatabricksMetastoreMetastoreInfo"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMetastoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMetastore.DataDatabricksMetastoreMetastoreInfo",
    jsii_struct_bases=[],
    name_mapping={
        "cloud": "cloud",
        "created_at": "createdAt",
        "created_by": "createdBy",
        "default_data_access_config_id": "defaultDataAccessConfigId",
        "delta_sharing_organization_name": "deltaSharingOrganizationName",
        "delta_sharing_recipient_token_lifetime_in_seconds": "deltaSharingRecipientTokenLifetimeInSeconds",
        "delta_sharing_scope": "deltaSharingScope",
        "external_access_enabled": "externalAccessEnabled",
        "global_metastore_id": "globalMetastoreId",
        "metastore_id": "metastoreId",
        "name": "name",
        "owner": "owner",
        "privilege_model_version": "privilegeModelVersion",
        "region": "region",
        "storage_root": "storageRoot",
        "storage_root_credential_id": "storageRootCredentialId",
        "storage_root_credential_name": "storageRootCredentialName",
        "updated_at": "updatedAt",
        "updated_by": "updatedBy",
    },
)
class DataDatabricksMetastoreMetastoreInfo:
    def __init__(
        self,
        *,
        cloud: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        default_data_access_config_id: typing.Optional[builtins.str] = None,
        delta_sharing_organization_name: typing.Optional[builtins.str] = None,
        delta_sharing_recipient_token_lifetime_in_seconds: typing.Optional[jsii.Number] = None,
        delta_sharing_scope: typing.Optional[builtins.str] = None,
        external_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        global_metastore_id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        privilege_model_version: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        storage_root: typing.Optional[builtins.str] = None,
        storage_root_credential_id: typing.Optional[builtins.str] = None,
        storage_root_credential_name: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#cloud DataDatabricksMetastore#cloud}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_at DataDatabricksMetastore#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_by DataDatabricksMetastore#created_by}.
        :param default_data_access_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#default_data_access_config_id DataDatabricksMetastore#default_data_access_config_id}.
        :param delta_sharing_organization_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_organization_name DataDatabricksMetastore#delta_sharing_organization_name}.
        :param delta_sharing_recipient_token_lifetime_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_recipient_token_lifetime_in_seconds DataDatabricksMetastore#delta_sharing_recipient_token_lifetime_in_seconds}.
        :param delta_sharing_scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_scope DataDatabricksMetastore#delta_sharing_scope}.
        :param external_access_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#external_access_enabled DataDatabricksMetastore#external_access_enabled}.
        :param global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#global_metastore_id DataDatabricksMetastore#global_metastore_id}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#owner DataDatabricksMetastore#owner}.
        :param privilege_model_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#privilege_model_version DataDatabricksMetastore#privilege_model_version}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.
        :param storage_root: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root DataDatabricksMetastore#storage_root}.
        :param storage_root_credential_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_id DataDatabricksMetastore#storage_root_credential_id}.
        :param storage_root_credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_name DataDatabricksMetastore#storage_root_credential_name}.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_at DataDatabricksMetastore#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_by DataDatabricksMetastore#updated_by}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db97a0ca17fe16cf7eaec922faf92dedc6d1971dd9485059dbe34564ce5330a8)
            check_type(argname="argument cloud", value=cloud, expected_type=type_hints["cloud"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument default_data_access_config_id", value=default_data_access_config_id, expected_type=type_hints["default_data_access_config_id"])
            check_type(argname="argument delta_sharing_organization_name", value=delta_sharing_organization_name, expected_type=type_hints["delta_sharing_organization_name"])
            check_type(argname="argument delta_sharing_recipient_token_lifetime_in_seconds", value=delta_sharing_recipient_token_lifetime_in_seconds, expected_type=type_hints["delta_sharing_recipient_token_lifetime_in_seconds"])
            check_type(argname="argument delta_sharing_scope", value=delta_sharing_scope, expected_type=type_hints["delta_sharing_scope"])
            check_type(argname="argument external_access_enabled", value=external_access_enabled, expected_type=type_hints["external_access_enabled"])
            check_type(argname="argument global_metastore_id", value=global_metastore_id, expected_type=type_hints["global_metastore_id"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument privilege_model_version", value=privilege_model_version, expected_type=type_hints["privilege_model_version"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument storage_root", value=storage_root, expected_type=type_hints["storage_root"])
            check_type(argname="argument storage_root_credential_id", value=storage_root_credential_id, expected_type=type_hints["storage_root_credential_id"])
            check_type(argname="argument storage_root_credential_name", value=storage_root_credential_name, expected_type=type_hints["storage_root_credential_name"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument updated_by", value=updated_by, expected_type=type_hints["updated_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud is not None:
            self._values["cloud"] = cloud
        if created_at is not None:
            self._values["created_at"] = created_at
        if created_by is not None:
            self._values["created_by"] = created_by
        if default_data_access_config_id is not None:
            self._values["default_data_access_config_id"] = default_data_access_config_id
        if delta_sharing_organization_name is not None:
            self._values["delta_sharing_organization_name"] = delta_sharing_organization_name
        if delta_sharing_recipient_token_lifetime_in_seconds is not None:
            self._values["delta_sharing_recipient_token_lifetime_in_seconds"] = delta_sharing_recipient_token_lifetime_in_seconds
        if delta_sharing_scope is not None:
            self._values["delta_sharing_scope"] = delta_sharing_scope
        if external_access_enabled is not None:
            self._values["external_access_enabled"] = external_access_enabled
        if global_metastore_id is not None:
            self._values["global_metastore_id"] = global_metastore_id
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner
        if privilege_model_version is not None:
            self._values["privilege_model_version"] = privilege_model_version
        if region is not None:
            self._values["region"] = region
        if storage_root is not None:
            self._values["storage_root"] = storage_root
        if storage_root_credential_id is not None:
            self._values["storage_root_credential_id"] = storage_root_credential_id
        if storage_root_credential_name is not None:
            self._values["storage_root_credential_name"] = storage_root_credential_name
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if updated_by is not None:
            self._values["updated_by"] = updated_by

    @builtins.property
    def cloud(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#cloud DataDatabricksMetastore#cloud}.'''
        result = self._values.get("cloud")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_at DataDatabricksMetastore#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#created_by DataDatabricksMetastore#created_by}.'''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_data_access_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#default_data_access_config_id DataDatabricksMetastore#default_data_access_config_id}.'''
        result = self._values.get("default_data_access_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delta_sharing_organization_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_organization_name DataDatabricksMetastore#delta_sharing_organization_name}.'''
        result = self._values.get("delta_sharing_organization_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delta_sharing_recipient_token_lifetime_in_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_recipient_token_lifetime_in_seconds DataDatabricksMetastore#delta_sharing_recipient_token_lifetime_in_seconds}.'''
        result = self._values.get("delta_sharing_recipient_token_lifetime_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delta_sharing_scope(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#delta_sharing_scope DataDatabricksMetastore#delta_sharing_scope}.'''
        result = self._values.get("delta_sharing_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_access_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#external_access_enabled DataDatabricksMetastore#external_access_enabled}.'''
        result = self._values.get("external_access_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#global_metastore_id DataDatabricksMetastore#global_metastore_id}.'''
        result = self._values.get("global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#metastore_id DataDatabricksMetastore#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#name DataDatabricksMetastore#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#owner DataDatabricksMetastore#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def privilege_model_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#privilege_model_version DataDatabricksMetastore#privilege_model_version}.'''
        result = self._values.get("privilege_model_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#region DataDatabricksMetastore#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_root(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root DataDatabricksMetastore#storage_root}.'''
        result = self._values.get("storage_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_root_credential_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_id DataDatabricksMetastore#storage_root_credential_id}.'''
        result = self._values.get("storage_root_credential_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_root_credential_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#storage_root_credential_name DataDatabricksMetastore#storage_root_credential_name}.'''
        result = self._values.get("storage_root_credential_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_at DataDatabricksMetastore#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def updated_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/metastore#updated_by DataDatabricksMetastore#updated_by}.'''
        result = self._values.get("updated_by")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMetastoreMetastoreInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksMetastoreMetastoreInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMetastore.DataDatabricksMetastoreMetastoreInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2397ff8e2fbd03fe918311a4581850c48236e6638267c0bad23e8d0c8467f352)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCloud")
    def reset_cloud(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloud", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetDefaultDataAccessConfigId")
    def reset_default_data_access_config_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultDataAccessConfigId", []))

    @jsii.member(jsii_name="resetDeltaSharingOrganizationName")
    def reset_delta_sharing_organization_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaSharingOrganizationName", []))

    @jsii.member(jsii_name="resetDeltaSharingRecipientTokenLifetimeInSeconds")
    def reset_delta_sharing_recipient_token_lifetime_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaSharingRecipientTokenLifetimeInSeconds", []))

    @jsii.member(jsii_name="resetDeltaSharingScope")
    def reset_delta_sharing_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaSharingScope", []))

    @jsii.member(jsii_name="resetExternalAccessEnabled")
    def reset_external_access_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalAccessEnabled", []))

    @jsii.member(jsii_name="resetGlobalMetastoreId")
    def reset_global_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalMetastoreId", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetPrivilegeModelVersion")
    def reset_privilege_model_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivilegeModelVersion", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetStorageRoot")
    def reset_storage_root(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageRoot", []))

    @jsii.member(jsii_name="resetStorageRootCredentialId")
    def reset_storage_root_credential_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageRootCredentialId", []))

    @jsii.member(jsii_name="resetStorageRootCredentialName")
    def reset_storage_root_credential_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageRootCredentialName", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUpdatedBy")
    def reset_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBy", []))

    @builtins.property
    @jsii.member(jsii_name="cloudInput")
    def cloud_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "createdAtInput"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataAccessConfigIdInput")
    def default_data_access_config_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultDataAccessConfigIdInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaSharingOrganizationNameInput")
    def delta_sharing_organization_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deltaSharingOrganizationNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaSharingRecipientTokenLifetimeInSecondsInput")
    def delta_sharing_recipient_token_lifetime_in_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deltaSharingRecipientTokenLifetimeInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaSharingScopeInput")
    def delta_sharing_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deltaSharingScopeInput"))

    @builtins.property
    @jsii.member(jsii_name="externalAccessEnabledInput")
    def external_access_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "externalAccessEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreIdInput")
    def global_metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalMetastoreIdInput"))

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
    @jsii.member(jsii_name="privilegeModelVersionInput")
    def privilege_model_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privilegeModelVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="storageRootCredentialIdInput")
    def storage_root_credential_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageRootCredentialIdInput"))

    @builtins.property
    @jsii.member(jsii_name="storageRootCredentialNameInput")
    def storage_root_credential_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageRootCredentialNameInput"))

    @builtins.property
    @jsii.member(jsii_name="storageRootInput")
    def storage_root_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageRootInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedByInput")
    def updated_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="cloud")
    def cloud(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloud"))

    @cloud.setter
    def cloud(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0250a9981f95922d333193ebe37762898a8afe4385d6897f0f934772aa59e21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloud", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed58fc4de13a03331caa0bfacfdb7ae3884eb6602eddb11ee03d278241d15780)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ade974845cfea1da6078fb7094bfc42dffb8c78ee8e57b46589e08ec532c46e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultDataAccessConfigId")
    def default_data_access_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultDataAccessConfigId"))

    @default_data_access_config_id.setter
    def default_data_access_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3ea47a3653ee0cdd92c826975fad060836863993e4e6028671c801800c86518)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultDataAccessConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deltaSharingOrganizationName")
    def delta_sharing_organization_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deltaSharingOrganizationName"))

    @delta_sharing_organization_name.setter
    def delta_sharing_organization_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088c4735699bb27f71d259bed850b0b4a45dc5b3695e42bfd48415dd6b3871ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deltaSharingOrganizationName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deltaSharingRecipientTokenLifetimeInSeconds")
    def delta_sharing_recipient_token_lifetime_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deltaSharingRecipientTokenLifetimeInSeconds"))

    @delta_sharing_recipient_token_lifetime_in_seconds.setter
    def delta_sharing_recipient_token_lifetime_in_seconds(
        self,
        value: jsii.Number,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3a4ba0e7b4c53409998fcaf3eb1bd4e92681db7ac535189c9e758b77699b19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deltaSharingRecipientTokenLifetimeInSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deltaSharingScope")
    def delta_sharing_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deltaSharingScope"))

    @delta_sharing_scope.setter
    def delta_sharing_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77eed0c66f547267fd40f069c4a9d34eaee65ea20c50cff03f5e8e679752d693)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deltaSharingScope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalAccessEnabled")
    def external_access_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "externalAccessEnabled"))

    @external_access_enabled.setter
    def external_access_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5613f99e1d3cdb30baca5137c84711201cd1529dcebea227ccec29b7034b761a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalAccessEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalMetastoreId")
    def global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalMetastoreId"))

    @global_metastore_id.setter
    def global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d709a28768c1220cc8dcc4dd93f5fac429ed8e1a38a130f530e95b1b689c146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalMetastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ced0c7b24363c7a81fbf44c6fe81f977f667bdc5f9fa2edf8bfb4750de235375)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f113753449d23b808ff71a6bed0745d025f4588f8f609b7e68554bcc75192d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb1188c0570b3897f62bf7181598d6e830171ead5725476005938c508a2a525e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privilegeModelVersion")
    def privilege_model_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privilegeModelVersion"))

    @privilege_model_version.setter
    def privilege_model_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46683fa0edf97957f09785ca88243136a9cabb93e551a0a9707e94618c2d70ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privilegeModelVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d2c8d787d65f38cd7778884e3adf8052db870da403a4e3c8f95f56b1176b3a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageRoot")
    def storage_root(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageRoot"))

    @storage_root.setter
    def storage_root(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6309438f3570c0ac90dc2f5364f5b64f444c40861936ab056a19a18be67b9f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageRoot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageRootCredentialId")
    def storage_root_credential_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageRootCredentialId"))

    @storage_root_credential_id.setter
    def storage_root_credential_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac3fb48aaa96532b09bb48b82230eaf984cb1846d0f2dbc4220c87620ae7744c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageRootCredentialId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageRootCredentialName")
    def storage_root_credential_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageRootCredentialName"))

    @storage_root_credential_name.setter
    def storage_root_credential_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b2ea94e0020f1208174b8f92c2ae13a7df0e5d01f015faa983d43abdd2e3dae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageRootCredentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09d826d4c89ac44a07a822661794791cb9b3ae28eacfaef06012d7ba97e5efc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @updated_by.setter
    def updated_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__405d266d28177d98a630a10b7fc0fb408bd2d49371bc8e28eee117b31b3cb185)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksMetastoreMetastoreInfo]:
        return typing.cast(typing.Optional[DataDatabricksMetastoreMetastoreInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMetastoreMetastoreInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df35006b2cf823d71e620f29a57ee6bdc7b5ce245891146f5d3d0739158f7412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksMetastore",
    "DataDatabricksMetastoreConfig",
    "DataDatabricksMetastoreMetastoreInfo",
    "DataDatabricksMetastoreMetastoreInfoOutputReference",
]

publication.publish()

def _typecheckingstub__92f4e4aba9b4143f5025d323ce738296d0534f71617907c1dadb4e8ee1a00f7f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    id: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    metastore_info: typing.Optional[typing.Union[DataDatabricksMetastoreMetastoreInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2c898dd205251d0f3e6801fe779c9c81b1cda37e04bdaafb3b30a333def38807(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdaea571b668c1c24b3a2c57a8ee15eabb7dc77892e9a12ecd4cf396d66d297e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2205a4c1d156165653d158f61d41b6818ce254924eb0aaf5684371fac3626f99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a1551961ce0ffd5a26b5b23c91a047fa6d2b0696eaacff63247397011cfa34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c818aae874b06d1e2a767b7e884694a1cf172be6c37731671d28e4604d8197(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14a89737b9b2fb44a530b283d85293e8619188e79e4ccdb6b035351e3d7425b9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    metastore_info: typing.Optional[typing.Union[DataDatabricksMetastoreMetastoreInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db97a0ca17fe16cf7eaec922faf92dedc6d1971dd9485059dbe34564ce5330a8(
    *,
    cloud: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[jsii.Number] = None,
    created_by: typing.Optional[builtins.str] = None,
    default_data_access_config_id: typing.Optional[builtins.str] = None,
    delta_sharing_organization_name: typing.Optional[builtins.str] = None,
    delta_sharing_recipient_token_lifetime_in_seconds: typing.Optional[jsii.Number] = None,
    delta_sharing_scope: typing.Optional[builtins.str] = None,
    external_access_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    global_metastore_id: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    privilege_model_version: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    storage_root: typing.Optional[builtins.str] = None,
    storage_root_credential_id: typing.Optional[builtins.str] = None,
    storage_root_credential_name: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[jsii.Number] = None,
    updated_by: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2397ff8e2fbd03fe918311a4581850c48236e6638267c0bad23e8d0c8467f352(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0250a9981f95922d333193ebe37762898a8afe4385d6897f0f934772aa59e21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed58fc4de13a03331caa0bfacfdb7ae3884eb6602eddb11ee03d278241d15780(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ade974845cfea1da6078fb7094bfc42dffb8c78ee8e57b46589e08ec532c46e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ea47a3653ee0cdd92c826975fad060836863993e4e6028671c801800c86518(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__088c4735699bb27f71d259bed850b0b4a45dc5b3695e42bfd48415dd6b3871ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3a4ba0e7b4c53409998fcaf3eb1bd4e92681db7ac535189c9e758b77699b19(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77eed0c66f547267fd40f069c4a9d34eaee65ea20c50cff03f5e8e679752d693(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5613f99e1d3cdb30baca5137c84711201cd1529dcebea227ccec29b7034b761a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d709a28768c1220cc8dcc4dd93f5fac429ed8e1a38a130f530e95b1b689c146(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ced0c7b24363c7a81fbf44c6fe81f977f667bdc5f9fa2edf8bfb4750de235375(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f113753449d23b808ff71a6bed0745d025f4588f8f609b7e68554bcc75192d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb1188c0570b3897f62bf7181598d6e830171ead5725476005938c508a2a525e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46683fa0edf97957f09785ca88243136a9cabb93e551a0a9707e94618c2d70ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d2c8d787d65f38cd7778884e3adf8052db870da403a4e3c8f95f56b1176b3a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6309438f3570c0ac90dc2f5364f5b64f444c40861936ab056a19a18be67b9f1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac3fb48aaa96532b09bb48b82230eaf984cb1846d0f2dbc4220c87620ae7744c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b2ea94e0020f1208174b8f92c2ae13a7df0e5d01f015faa983d43abdd2e3dae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09d826d4c89ac44a07a822661794791cb9b3ae28eacfaef06012d7ba97e5efc4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__405d266d28177d98a630a10b7fc0fb408bd2d49371bc8e28eee117b31b3cb185(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df35006b2cf823d71e620f29a57ee6bdc7b5ce245891146f5d3d0739158f7412(
    value: typing.Optional[DataDatabricksMetastoreMetastoreInfo],
) -> None:
    """Type checking stubs"""
    pass
