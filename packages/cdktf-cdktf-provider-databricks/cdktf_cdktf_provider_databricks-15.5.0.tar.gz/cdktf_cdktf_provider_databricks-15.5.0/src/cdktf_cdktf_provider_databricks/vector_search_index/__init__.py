r'''
# `databricks_vector_search_index`

Refer to the Terraform Registry for docs: [`databricks_vector_search_index`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index).
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


class VectorSearchIndex(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndex",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index databricks_vector_search_index}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        endpoint_name: builtins.str,
        index_type: builtins.str,
        name: builtins.str,
        primary_key: builtins.str,
        delta_sync_index_spec: typing.Optional[typing.Union["VectorSearchIndexDeltaSyncIndexSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        direct_access_index_spec: typing.Optional[typing.Union["VectorSearchIndexDirectAccessIndexSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VectorSearchIndexTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index databricks_vector_search_index} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#endpoint_name VectorSearchIndex#endpoint_name}.
        :param index_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#index_type VectorSearchIndex#index_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        :param primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#primary_key VectorSearchIndex#primary_key}.
        :param delta_sync_index_spec: delta_sync_index_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#delta_sync_index_spec VectorSearchIndex#delta_sync_index_spec}
        :param direct_access_index_spec: direct_access_index_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#direct_access_index_spec VectorSearchIndex#direct_access_index_spec}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#id VectorSearchIndex#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#timeouts VectorSearchIndex#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__711c2c98bce26e99f92e38e11b2082ba59ead1ee481737ee4126f8f94bdd4d37)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VectorSearchIndexConfig(
            endpoint_name=endpoint_name,
            index_type=index_type,
            name=name,
            primary_key=primary_key,
            delta_sync_index_spec=delta_sync_index_spec,
            direct_access_index_spec=direct_access_index_spec,
            id=id,
            timeouts=timeouts,
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
        '''Generates CDKTF code for importing a VectorSearchIndex resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VectorSearchIndex to import.
        :param import_from_id: The id of the existing VectorSearchIndex that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VectorSearchIndex to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4d1d2397b8b4b45762471699f05ab560b3f415f244572784802fed320129218)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDeltaSyncIndexSpec")
    def put_delta_sync_index_spec(
        self,
        *,
        embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_writeback_table: typing.Optional[builtins.str] = None,
        pipeline_type: typing.Optional[builtins.str] = None,
        source_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_source_columns: embedding_source_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        :param embedding_vector_columns: embedding_vector_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        :param embedding_writeback_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_writeback_table VectorSearchIndex#embedding_writeback_table}.
        :param pipeline_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#pipeline_type VectorSearchIndex#pipeline_type}.
        :param source_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#source_table VectorSearchIndex#source_table}.
        '''
        value = VectorSearchIndexDeltaSyncIndexSpec(
            embedding_source_columns=embedding_source_columns,
            embedding_vector_columns=embedding_vector_columns,
            embedding_writeback_table=embedding_writeback_table,
            pipeline_type=pipeline_type,
            source_table=source_table,
        )

        return typing.cast(None, jsii.invoke(self, "putDeltaSyncIndexSpec", [value]))

    @jsii.member(jsii_name="putDirectAccessIndexSpec")
    def put_direct_access_index_spec(
        self,
        *,
        embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        schema_json: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_source_columns: embedding_source_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        :param embedding_vector_columns: embedding_vector_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        :param schema_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#schema_json VectorSearchIndex#schema_json}.
        '''
        value = VectorSearchIndexDirectAccessIndexSpec(
            embedding_source_columns=embedding_source_columns,
            embedding_vector_columns=embedding_vector_columns,
            schema_json=schema_json,
        )

        return typing.cast(None, jsii.invoke(self, "putDirectAccessIndexSpec", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#create VectorSearchIndex#create}.
        '''
        value = VectorSearchIndexTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDeltaSyncIndexSpec")
    def reset_delta_sync_index_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaSyncIndexSpec", []))

    @jsii.member(jsii_name="resetDirectAccessIndexSpec")
    def reset_direct_access_index_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectAccessIndexSpec", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="deltaSyncIndexSpec")
    def delta_sync_index_spec(
        self,
    ) -> "VectorSearchIndexDeltaSyncIndexSpecOutputReference":
        return typing.cast("VectorSearchIndexDeltaSyncIndexSpecOutputReference", jsii.get(self, "deltaSyncIndexSpec"))

    @builtins.property
    @jsii.member(jsii_name="directAccessIndexSpec")
    def direct_access_index_spec(
        self,
    ) -> "VectorSearchIndexDirectAccessIndexSpecOutputReference":
        return typing.cast("VectorSearchIndexDirectAccessIndexSpecOutputReference", jsii.get(self, "directAccessIndexSpec"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "VectorSearchIndexStatusList":
        return typing.cast("VectorSearchIndexStatusList", jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "VectorSearchIndexTimeoutsOutputReference":
        return typing.cast("VectorSearchIndexTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="deltaSyncIndexSpecInput")
    def delta_sync_index_spec_input(
        self,
    ) -> typing.Optional["VectorSearchIndexDeltaSyncIndexSpec"]:
        return typing.cast(typing.Optional["VectorSearchIndexDeltaSyncIndexSpec"], jsii.get(self, "deltaSyncIndexSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="directAccessIndexSpecInput")
    def direct_access_index_spec_input(
        self,
    ) -> typing.Optional["VectorSearchIndexDirectAccessIndexSpec"]:
        return typing.cast(typing.Optional["VectorSearchIndexDirectAccessIndexSpec"], jsii.get(self, "directAccessIndexSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointNameInput")
    def endpoint_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="indexTypeInput")
    def index_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeyInput")
    def primary_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "primaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VectorSearchIndexTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VectorSearchIndexTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @endpoint_name.setter
    def endpoint_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06aa692a3bb3010e2c4eacfd104e1bf8e07ce546cf964a3751c1ddeba8da255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31cfbfe29c004005036ef1e1ba8013c7eb85bf5a65c2079cdee622a0b01d39d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indexType")
    def index_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexType"))

    @index_type.setter
    def index_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92cfcd757f9cee25d5ba4375de986d26b123c0a892ebe6ba25509acc6227cba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b960b63beef0cde54763552d779b2cd981c2a474766ed69e0a2da51775bc216b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKey")
    def primary_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryKey"))

    @primary_key.setter
    def primary_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__970eab4f5359aecda3375d8e1dee6545e5b8fd3ed9ebbe3e511b3d0be9218aa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKey", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "endpoint_name": "endpointName",
        "index_type": "indexType",
        "name": "name",
        "primary_key": "primaryKey",
        "delta_sync_index_spec": "deltaSyncIndexSpec",
        "direct_access_index_spec": "directAccessIndexSpec",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class VectorSearchIndexConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        endpoint_name: builtins.str,
        index_type: builtins.str,
        name: builtins.str,
        primary_key: builtins.str,
        delta_sync_index_spec: typing.Optional[typing.Union["VectorSearchIndexDeltaSyncIndexSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        direct_access_index_spec: typing.Optional[typing.Union["VectorSearchIndexDirectAccessIndexSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VectorSearchIndexTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#endpoint_name VectorSearchIndex#endpoint_name}.
        :param index_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#index_type VectorSearchIndex#index_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        :param primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#primary_key VectorSearchIndex#primary_key}.
        :param delta_sync_index_spec: delta_sync_index_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#delta_sync_index_spec VectorSearchIndex#delta_sync_index_spec}
        :param direct_access_index_spec: direct_access_index_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#direct_access_index_spec VectorSearchIndex#direct_access_index_spec}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#id VectorSearchIndex#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#timeouts VectorSearchIndex#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(delta_sync_index_spec, dict):
            delta_sync_index_spec = VectorSearchIndexDeltaSyncIndexSpec(**delta_sync_index_spec)
        if isinstance(direct_access_index_spec, dict):
            direct_access_index_spec = VectorSearchIndexDirectAccessIndexSpec(**direct_access_index_spec)
        if isinstance(timeouts, dict):
            timeouts = VectorSearchIndexTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6948600f4627cd62855d03ff3234112015ad0b8e183f1bc0e091b0093b3d97a4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument index_type", value=index_type, expected_type=type_hints["index_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument primary_key", value=primary_key, expected_type=type_hints["primary_key"])
            check_type(argname="argument delta_sync_index_spec", value=delta_sync_index_spec, expected_type=type_hints["delta_sync_index_spec"])
            check_type(argname="argument direct_access_index_spec", value=direct_access_index_spec, expected_type=type_hints["direct_access_index_spec"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoint_name": endpoint_name,
            "index_type": index_type,
            "name": name,
            "primary_key": primary_key,
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
        if delta_sync_index_spec is not None:
            self._values["delta_sync_index_spec"] = delta_sync_index_spec
        if direct_access_index_spec is not None:
            self._values["direct_access_index_spec"] = direct_access_index_spec
        if id is not None:
            self._values["id"] = id
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def endpoint_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#endpoint_name VectorSearchIndex#endpoint_name}.'''
        result = self._values.get("endpoint_name")
        assert result is not None, "Required property 'endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#index_type VectorSearchIndex#index_type}.'''
        result = self._values.get("index_type")
        assert result is not None, "Required property 'index_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#primary_key VectorSearchIndex#primary_key}.'''
        result = self._values.get("primary_key")
        assert result is not None, "Required property 'primary_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delta_sync_index_spec(
        self,
    ) -> typing.Optional["VectorSearchIndexDeltaSyncIndexSpec"]:
        '''delta_sync_index_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#delta_sync_index_spec VectorSearchIndex#delta_sync_index_spec}
        '''
        result = self._values.get("delta_sync_index_spec")
        return typing.cast(typing.Optional["VectorSearchIndexDeltaSyncIndexSpec"], result)

    @builtins.property
    def direct_access_index_spec(
        self,
    ) -> typing.Optional["VectorSearchIndexDirectAccessIndexSpec"]:
        '''direct_access_index_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#direct_access_index_spec VectorSearchIndex#direct_access_index_spec}
        '''
        result = self._values.get("direct_access_index_spec")
        return typing.cast(typing.Optional["VectorSearchIndexDirectAccessIndexSpec"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#id VectorSearchIndex#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["VectorSearchIndexTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#timeouts VectorSearchIndex#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["VectorSearchIndexTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpec",
    jsii_struct_bases=[],
    name_mapping={
        "embedding_source_columns": "embeddingSourceColumns",
        "embedding_vector_columns": "embeddingVectorColumns",
        "embedding_writeback_table": "embeddingWritebackTable",
        "pipeline_type": "pipelineType",
        "source_table": "sourceTable",
    },
)
class VectorSearchIndexDeltaSyncIndexSpec:
    def __init__(
        self,
        *,
        embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_writeback_table: typing.Optional[builtins.str] = None,
        pipeline_type: typing.Optional[builtins.str] = None,
        source_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_source_columns: embedding_source_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        :param embedding_vector_columns: embedding_vector_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        :param embedding_writeback_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_writeback_table VectorSearchIndex#embedding_writeback_table}.
        :param pipeline_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#pipeline_type VectorSearchIndex#pipeline_type}.
        :param source_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#source_table VectorSearchIndex#source_table}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__022daafaad134b4e3ca64c58d7359b2b6603ccfa3105580f61d74d77ff0a1c44)
            check_type(argname="argument embedding_source_columns", value=embedding_source_columns, expected_type=type_hints["embedding_source_columns"])
            check_type(argname="argument embedding_vector_columns", value=embedding_vector_columns, expected_type=type_hints["embedding_vector_columns"])
            check_type(argname="argument embedding_writeback_table", value=embedding_writeback_table, expected_type=type_hints["embedding_writeback_table"])
            check_type(argname="argument pipeline_type", value=pipeline_type, expected_type=type_hints["pipeline_type"])
            check_type(argname="argument source_table", value=source_table, expected_type=type_hints["source_table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_source_columns is not None:
            self._values["embedding_source_columns"] = embedding_source_columns
        if embedding_vector_columns is not None:
            self._values["embedding_vector_columns"] = embedding_vector_columns
        if embedding_writeback_table is not None:
            self._values["embedding_writeback_table"] = embedding_writeback_table
        if pipeline_type is not None:
            self._values["pipeline_type"] = pipeline_type
        if source_table is not None:
            self._values["source_table"] = source_table

    @builtins.property
    def embedding_source_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns"]]]:
        '''embedding_source_columns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        '''
        result = self._values.get("embedding_source_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns"]]], result)

    @builtins.property
    def embedding_vector_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns"]]]:
        '''embedding_vector_columns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        '''
        result = self._values.get("embedding_vector_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns"]]], result)

    @builtins.property
    def embedding_writeback_table(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_writeback_table VectorSearchIndex#embedding_writeback_table}.'''
        result = self._values.get("embedding_writeback_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#pipeline_type VectorSearchIndex#pipeline_type}.'''
        result = self._values.get("pipeline_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_table(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#source_table VectorSearchIndex#source_table}.'''
        result = self._values.get("source_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDeltaSyncIndexSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns",
    jsii_struct_bases=[],
    name_mapping={
        "embedding_model_endpoint_name": "embeddingModelEndpointName",
        "model_endpoint_name_for_query": "modelEndpointNameForQuery",
        "name": "name",
    },
)
class VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns:
    def __init__(
        self,
        *,
        embedding_model_endpoint_name: typing.Optional[builtins.str] = None,
        model_endpoint_name_for_query: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_model_endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_model_endpoint_name VectorSearchIndex#embedding_model_endpoint_name}.
        :param model_endpoint_name_for_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#model_endpoint_name_for_query VectorSearchIndex#model_endpoint_name_for_query}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc196a6bad19cd59dcc12865e40d6977a038464cd63dc5771acea84ceac59e3)
            check_type(argname="argument embedding_model_endpoint_name", value=embedding_model_endpoint_name, expected_type=type_hints["embedding_model_endpoint_name"])
            check_type(argname="argument model_endpoint_name_for_query", value=model_endpoint_name_for_query, expected_type=type_hints["model_endpoint_name_for_query"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_model_endpoint_name is not None:
            self._values["embedding_model_endpoint_name"] = embedding_model_endpoint_name
        if model_endpoint_name_for_query is not None:
            self._values["model_endpoint_name_for_query"] = model_endpoint_name_for_query
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def embedding_model_endpoint_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_model_endpoint_name VectorSearchIndex#embedding_model_endpoint_name}.'''
        result = self._values.get("embedding_model_endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def model_endpoint_name_for_query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#model_endpoint_name_for_query VectorSearchIndex#model_endpoint_name_for_query}.'''
        result = self._values.get("model_endpoint_name_for_query")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7bfcccaf0a7a8869597bc041cdcf634ce8301413b30056dbd3b638334478b909)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__071c6f67b2bd48e7339212b7b8b7b50492aff07f54fad9836a74588fe9440de8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e607529f9b6bd1a033fb8936ddf4cfe3e7324ae97379fc15ae0c60524c0f2f03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__af0d138c20907c18891de046ee71a543477b63691e0b236bb705983a06b2d6f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5887b2fbe29f2fe97bf6c37afecf7b58f72e9ada6f2670281fa76bb971ed4969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc02e10c6f63088f43c6d948beea13a6a27876a19f8029c25e151c9467f19a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2af0293b8e76cdd5c2513e551ff0a809acab2ad17ce460ab1da4648985be4a0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmbeddingModelEndpointName")
    def reset_embedding_model_endpoint_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingModelEndpointName", []))

    @jsii.member(jsii_name="resetModelEndpointNameForQuery")
    def reset_model_endpoint_name_for_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelEndpointNameForQuery", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelEndpointNameInput")
    def embedding_model_endpoint_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingModelEndpointNameInput"))

    @builtins.property
    @jsii.member(jsii_name="modelEndpointNameForQueryInput")
    def model_endpoint_name_for_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelEndpointNameForQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelEndpointName")
    def embedding_model_endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelEndpointName"))

    @embedding_model_endpoint_name.setter
    def embedding_model_endpoint_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66da0438965a52c0e279430cdb4875df3559d427ec153d3bf7b45c08adf00d05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingModelEndpointName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelEndpointNameForQuery")
    def model_endpoint_name_for_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelEndpointNameForQuery"))

    @model_endpoint_name_for_query.setter
    def model_endpoint_name_for_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d420c2f332dfeba08149bbfd72dc504583fe4af55f12662fae5429348f88ad7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelEndpointNameForQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11239aad44eb38667bec58a54bd4d44c271211d32c42ce6f5e8b645b6022d487)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ed2677a1c5e81c5aa3da8953cee7f07ec1996d721d50146f2095d727b4ac28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns",
    jsii_struct_bases=[],
    name_mapping={"embedding_dimension": "embeddingDimension", "name": "name"},
)
class VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns:
    def __init__(
        self,
        *,
        embedding_dimension: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_dimension: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_dimension VectorSearchIndex#embedding_dimension}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfca5f52c24720a8eaa0e5eb000460d37e10cbd5001763609febbd35c1c7666a)
            check_type(argname="argument embedding_dimension", value=embedding_dimension, expected_type=type_hints["embedding_dimension"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_dimension is not None:
            self._values["embedding_dimension"] = embedding_dimension
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def embedding_dimension(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_dimension VectorSearchIndex#embedding_dimension}.'''
        result = self._values.get("embedding_dimension")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f0e4ef55669c181d2c9b1731aeff47cc12b3d54874ccd135a7b518d928c90fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e39513701d797e887890e21ca4d22bbbe29140f9f4aee36b6d86c74b03071a1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ade831f62f672d2e9fe41bd79ab6a161ca4e22695656ee1533a02cfe5e4819)
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
            type_hints = typing.get_type_hints(_typecheckingstub__23246593f2557c8110d30bcd693cf78dcab3e7aa143baaedc1828e2d83568d79)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bf304163263c8d9c898c451ab6c520cc0110cafe1223e6049c05c40ef1c0fcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f12b53d4f453005d76b749b5298c4c12c423823c346a067ee421eda081c4412e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4eba59fd5207d4a95158b28d78a6978c00ce7631758cecbb0010058d42e6e151)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmbeddingDimension")
    def reset_embedding_dimension(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingDimension", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingDimensionInput")
    def embedding_dimension_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "embeddingDimensionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingDimension")
    def embedding_dimension(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "embeddingDimension"))

    @embedding_dimension.setter
    def embedding_dimension(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69466ae66649b1f7596d5e76d43eedc196daf78ca9eb722f1037e6b1d1ba7a5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingDimension", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3cf8628eea5382792b440308a454cb9e18069fb92088dd2fa6473b551db9255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d09be432791edd8791b7beaca2d027138d6dea0d14f600ea4897981bdbb737bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDeltaSyncIndexSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDeltaSyncIndexSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d42372c6682813f7cdc453673793df9270b15d3ba717ac25b63fef33fe1402f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEmbeddingSourceColumns")
    def put_embedding_source_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b8f3d3f77cffca224b83947da1ce9524cfaefd7ef6a11d19a36b530aed3a79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmbeddingSourceColumns", [value]))

    @jsii.member(jsii_name="putEmbeddingVectorColumns")
    def put_embedding_vector_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__992ad469a204083eff4e8f8c9f26565018a1849c69a5a2fd3cfa47e6c68a2e0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmbeddingVectorColumns", [value]))

    @jsii.member(jsii_name="resetEmbeddingSourceColumns")
    def reset_embedding_source_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingSourceColumns", []))

    @jsii.member(jsii_name="resetEmbeddingVectorColumns")
    def reset_embedding_vector_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingVectorColumns", []))

    @jsii.member(jsii_name="resetEmbeddingWritebackTable")
    def reset_embedding_writeback_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingWritebackTable", []))

    @jsii.member(jsii_name="resetPipelineType")
    def reset_pipeline_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineType", []))

    @jsii.member(jsii_name="resetSourceTable")
    def reset_source_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceTable", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingSourceColumns")
    def embedding_source_columns(
        self,
    ) -> VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsList:
        return typing.cast(VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsList, jsii.get(self, "embeddingSourceColumns"))

    @builtins.property
    @jsii.member(jsii_name="embeddingVectorColumns")
    def embedding_vector_columns(
        self,
    ) -> VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsList:
        return typing.cast(VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsList, jsii.get(self, "embeddingVectorColumns"))

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @builtins.property
    @jsii.member(jsii_name="embeddingSourceColumnsInput")
    def embedding_source_columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]], jsii.get(self, "embeddingSourceColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingVectorColumnsInput")
    def embedding_vector_columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]], jsii.get(self, "embeddingVectorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingWritebackTableInput")
    def embedding_writeback_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingWritebackTableInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineTypeInput")
    def pipeline_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTableInput")
    def source_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTableInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingWritebackTable")
    def embedding_writeback_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingWritebackTable"))

    @embedding_writeback_table.setter
    def embedding_writeback_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60db1f3d98763481b73841cc14c2656482e3855f9804ba41c40214f05f9312a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingWritebackTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineType")
    def pipeline_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineType"))

    @pipeline_type.setter
    def pipeline_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d2451938ee58ed05825fcc1a85e795cd064d76c494f0bf246769f392f17da7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTable")
    def source_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTable"))

    @source_table.setter
    def source_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1c24b9cf078f5a639560c06c8b1c457f05c325bd5fc35a2ca2e023fbe787bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VectorSearchIndexDeltaSyncIndexSpec]:
        return typing.cast(typing.Optional[VectorSearchIndexDeltaSyncIndexSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VectorSearchIndexDeltaSyncIndexSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a28fafeda0bdfbe976c6c93c44fe4b9cf43c53a4c1b50a73fa864669ff3380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpec",
    jsii_struct_bases=[],
    name_mapping={
        "embedding_source_columns": "embeddingSourceColumns",
        "embedding_vector_columns": "embeddingVectorColumns",
        "schema_json": "schemaJson",
    },
)
class VectorSearchIndexDirectAccessIndexSpec:
    def __init__(
        self,
        *,
        embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        schema_json: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_source_columns: embedding_source_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        :param embedding_vector_columns: embedding_vector_columns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        :param schema_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#schema_json VectorSearchIndex#schema_json}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c32d6e9f6680a2641c1416371b599d1f83300cbc488852ca0fd4604c2460148)
            check_type(argname="argument embedding_source_columns", value=embedding_source_columns, expected_type=type_hints["embedding_source_columns"])
            check_type(argname="argument embedding_vector_columns", value=embedding_vector_columns, expected_type=type_hints["embedding_vector_columns"])
            check_type(argname="argument schema_json", value=schema_json, expected_type=type_hints["schema_json"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_source_columns is not None:
            self._values["embedding_source_columns"] = embedding_source_columns
        if embedding_vector_columns is not None:
            self._values["embedding_vector_columns"] = embedding_vector_columns
        if schema_json is not None:
            self._values["schema_json"] = schema_json

    @builtins.property
    def embedding_source_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns"]]]:
        '''embedding_source_columns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_source_columns VectorSearchIndex#embedding_source_columns}
        '''
        result = self._values.get("embedding_source_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns"]]], result)

    @builtins.property
    def embedding_vector_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns"]]]:
        '''embedding_vector_columns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_vector_columns VectorSearchIndex#embedding_vector_columns}
        '''
        result = self._values.get("embedding_vector_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns"]]], result)

    @builtins.property
    def schema_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#schema_json VectorSearchIndex#schema_json}.'''
        result = self._values.get("schema_json")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDirectAccessIndexSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns",
    jsii_struct_bases=[],
    name_mapping={
        "embedding_model_endpoint_name": "embeddingModelEndpointName",
        "model_endpoint_name_for_query": "modelEndpointNameForQuery",
        "name": "name",
    },
)
class VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns:
    def __init__(
        self,
        *,
        embedding_model_endpoint_name: typing.Optional[builtins.str] = None,
        model_endpoint_name_for_query: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_model_endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_model_endpoint_name VectorSearchIndex#embedding_model_endpoint_name}.
        :param model_endpoint_name_for_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#model_endpoint_name_for_query VectorSearchIndex#model_endpoint_name_for_query}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0409f064172e233053af15ac516c3a6accc6cf0c5d64aee774859d39494f8419)
            check_type(argname="argument embedding_model_endpoint_name", value=embedding_model_endpoint_name, expected_type=type_hints["embedding_model_endpoint_name"])
            check_type(argname="argument model_endpoint_name_for_query", value=model_endpoint_name_for_query, expected_type=type_hints["model_endpoint_name_for_query"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_model_endpoint_name is not None:
            self._values["embedding_model_endpoint_name"] = embedding_model_endpoint_name
        if model_endpoint_name_for_query is not None:
            self._values["model_endpoint_name_for_query"] = model_endpoint_name_for_query
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def embedding_model_endpoint_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_model_endpoint_name VectorSearchIndex#embedding_model_endpoint_name}.'''
        result = self._values.get("embedding_model_endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def model_endpoint_name_for_query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#model_endpoint_name_for_query VectorSearchIndex#model_endpoint_name_for_query}.'''
        result = self._values.get("model_endpoint_name_for_query")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0915fa5419f5fca105b84fee74fa653a3edae4a193c52e7c271f31fc7e159a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef26a729c2e8e0613f848934cd127da4682612e9115c41fad8e5e459e37be4ae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eddcbcc686ef75633687f1390b185dbf3851044760862807f84b2dea8eb9508)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fffa5664c78991da340294f46a1f770cf3febecbbf2414e7adf573cf2e97a5d5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__24958ab483d540e1d55753735d3c2b19fb1435ec94eeeb8cd3456779048543f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__513e274fb2dace55da22d15124f8c17cf489aefa4f6528546e76321244d78635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b27e0274c839f9ad99491e55028732f0bf78be9bb7337ebd5e765497e55e4073)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmbeddingModelEndpointName")
    def reset_embedding_model_endpoint_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingModelEndpointName", []))

    @jsii.member(jsii_name="resetModelEndpointNameForQuery")
    def reset_model_endpoint_name_for_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelEndpointNameForQuery", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelEndpointNameInput")
    def embedding_model_endpoint_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingModelEndpointNameInput"))

    @builtins.property
    @jsii.member(jsii_name="modelEndpointNameForQueryInput")
    def model_endpoint_name_for_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelEndpointNameForQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelEndpointName")
    def embedding_model_endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelEndpointName"))

    @embedding_model_endpoint_name.setter
    def embedding_model_endpoint_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433829bb84799fc571d8f8f7bceec0258624872194dcfaba387bb0ba975ff72a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingModelEndpointName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelEndpointNameForQuery")
    def model_endpoint_name_for_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelEndpointNameForQuery"))

    @model_endpoint_name_for_query.setter
    def model_endpoint_name_for_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1349a202214dcd0143ba13aeae08a7b6e64b6f3cca71d108f72392dc56f277)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelEndpointNameForQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af8931d3f6df07702d3dd0d1c321bb8b95d8e2077ee7a0d0df1fbe9b4f1964b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dee08e5f33083e985bec81ff4d4b6bfe0e4db2a6a1397662e9fb8468c6ade92c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns",
    jsii_struct_bases=[],
    name_mapping={"embedding_dimension": "embeddingDimension", "name": "name"},
)
class VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns:
    def __init__(
        self,
        *,
        embedding_dimension: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_dimension: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_dimension VectorSearchIndex#embedding_dimension}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e5ea5ac7e187729377f403c1c2ec6c5f9ceaca31be22e8727b0f329b2608a0)
            check_type(argname="argument embedding_dimension", value=embedding_dimension, expected_type=type_hints["embedding_dimension"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if embedding_dimension is not None:
            self._values["embedding_dimension"] = embedding_dimension
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def embedding_dimension(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#embedding_dimension VectorSearchIndex#embedding_dimension}.'''
        result = self._values.get("embedding_dimension")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#name VectorSearchIndex#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba08be7fc4f4c953fdc7a5338020ad5a8bb4a8327d551d700a0ad88ff54f4f64)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d060f9e4542035fbdc424346d11ba25f784d7fa53283428ec4beef12d3bfb0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0158fbce68b5aee24179768ac6785ef5d3180ef1744409baab7f7bce857723c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ee7b1052b41563f7d1799f4d4e37e5c45967d868111ce40f5e0051789e6da05)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7fadf2a672c6d67b6aae6033197bf759e306c89d5efdcdcfcb2ce6396baac825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e2548d59a30f576bf00e4deedf3948d12339f902341f7342ed3fffe3c7c895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2778cd602e2370e14a17cb97e1bbe75560d8837c5cc0c13f0e67bd9099879d5f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEmbeddingDimension")
    def reset_embedding_dimension(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingDimension", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingDimensionInput")
    def embedding_dimension_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "embeddingDimensionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingDimension")
    def embedding_dimension(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "embeddingDimension"))

    @embedding_dimension.setter
    def embedding_dimension(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568fcb1bb49f93fde783dc5d8c60bb41baab04fed58fa496e9e3645401ba949c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingDimension", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42e4e6a5d7fb40d15848f915adfe1809376180d84ce3af5aacf6a56d97c43620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f37bca937d18c6d3c81772c7adaddc337972dcc65cd6ee32ee2f5e4b6c2dd7e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexDirectAccessIndexSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexDirectAccessIndexSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f8c5ad5b634127aa7c7e71e18e9ec1d8ce468e2fe1dbec2850be9fc1b821d07)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEmbeddingSourceColumns")
    def put_embedding_source_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04e70b4afdaeb076f13cbb7e378db04d1808aaca658bf77c971a4c126ae6f4ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmbeddingSourceColumns", [value]))

    @jsii.member(jsii_name="putEmbeddingVectorColumns")
    def put_embedding_vector_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d2ceb0b30dbd1d89bb9a4cee5de650ceded34c681d09525e3054b7903653f21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmbeddingVectorColumns", [value]))

    @jsii.member(jsii_name="resetEmbeddingSourceColumns")
    def reset_embedding_source_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingSourceColumns", []))

    @jsii.member(jsii_name="resetEmbeddingVectorColumns")
    def reset_embedding_vector_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingVectorColumns", []))

    @jsii.member(jsii_name="resetSchemaJson")
    def reset_schema_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchemaJson", []))

    @builtins.property
    @jsii.member(jsii_name="embeddingSourceColumns")
    def embedding_source_columns(
        self,
    ) -> VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsList:
        return typing.cast(VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsList, jsii.get(self, "embeddingSourceColumns"))

    @builtins.property
    @jsii.member(jsii_name="embeddingVectorColumns")
    def embedding_vector_columns(
        self,
    ) -> VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsList:
        return typing.cast(VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsList, jsii.get(self, "embeddingVectorColumns"))

    @builtins.property
    @jsii.member(jsii_name="embeddingSourceColumnsInput")
    def embedding_source_columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]], jsii.get(self, "embeddingSourceColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingVectorColumnsInput")
    def embedding_vector_columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]], jsii.get(self, "embeddingVectorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaJsonInput")
    def schema_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaJson")
    def schema_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schemaJson"))

    @schema_json.setter
    def schema_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955ab7e7bb2acd047dd6ce712c6bebdae7fd890baccd96ba477ff44f0ca7ae0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VectorSearchIndexDirectAccessIndexSpec]:
        return typing.cast(typing.Optional[VectorSearchIndexDirectAccessIndexSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VectorSearchIndexDirectAccessIndexSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e986bd8eacf4780cd27a028ff1d7d8a0dab2ab87c1d834c692feff00d6ffd231)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexStatus",
    jsii_struct_bases=[],
    name_mapping={},
)
class VectorSearchIndexStatus:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexStatusList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexStatusList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__978988ace88a078f64f255cf8c66781775dfa9709cdce9e3df5b47f51078730f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VectorSearchIndexStatusOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9eb45fc8cd280c747c115f8700b035f263d46a6a8a8324c4029731e50920f1d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VectorSearchIndexStatusOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c8665c29f1712488101bc91858697dfcc89c9cf409d53f20787c491f5ed74eb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd3fe1cd5e16f8c2320d12f9cf2a0272dd310335ff475ba3c64ae44ec1f395d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57010a49fa5e1ba72ded99efb83c73999b605085792b73dc9ff02a2b2a7b03bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class VectorSearchIndexStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23b7df296d1526bca88367d72b2821f03049e6ac81770d839c9933f5c5bbd4d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="indexedRowCount")
    def indexed_row_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indexedRowCount"))

    @builtins.property
    @jsii.member(jsii_name="indexUrl")
    def index_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexUrl"))

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @builtins.property
    @jsii.member(jsii_name="ready")
    def ready(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ready"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VectorSearchIndexStatus]:
        return typing.cast(typing.Optional[VectorSearchIndexStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VectorSearchIndexStatus]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffe5db9c0390095125a571817ddf2c5c25ddca800c3a7a7ee5a5a009d14f27a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class VectorSearchIndexTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#create VectorSearchIndex#create}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__283520b3fe14bfaddb20c7ffcbb6dfbf7e9505286dc01a987123452ebee5bf38)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/vector_search_index#create VectorSearchIndex#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorSearchIndexTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VectorSearchIndexTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.vectorSearchIndex.VectorSearchIndexTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55318db47e587306f3e5486cd2730a92104933a4c01ff4d847aa98a384e04e14)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff0aa6c998f9c065bbf095078eccc8ecddac5937f52a9cb02fc6a351fdf5ae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a6440b4936a0cd3c17ce447399610d5bbd1f9d37180f3ddec2fba1cd1236c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "VectorSearchIndex",
    "VectorSearchIndexConfig",
    "VectorSearchIndexDeltaSyncIndexSpec",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsList",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumnsOutputReference",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsList",
    "VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumnsOutputReference",
    "VectorSearchIndexDeltaSyncIndexSpecOutputReference",
    "VectorSearchIndexDirectAccessIndexSpec",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsList",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumnsOutputReference",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsList",
    "VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumnsOutputReference",
    "VectorSearchIndexDirectAccessIndexSpecOutputReference",
    "VectorSearchIndexStatus",
    "VectorSearchIndexStatusList",
    "VectorSearchIndexStatusOutputReference",
    "VectorSearchIndexTimeouts",
    "VectorSearchIndexTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__711c2c98bce26e99f92e38e11b2082ba59ead1ee481737ee4126f8f94bdd4d37(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    endpoint_name: builtins.str,
    index_type: builtins.str,
    name: builtins.str,
    primary_key: builtins.str,
    delta_sync_index_spec: typing.Optional[typing.Union[VectorSearchIndexDeltaSyncIndexSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    direct_access_index_spec: typing.Optional[typing.Union[VectorSearchIndexDirectAccessIndexSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VectorSearchIndexTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__a4d1d2397b8b4b45762471699f05ab560b3f415f244572784802fed320129218(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06aa692a3bb3010e2c4eacfd104e1bf8e07ce546cf964a3751c1ddeba8da255(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31cfbfe29c004005036ef1e1ba8013c7eb85bf5a65c2079cdee622a0b01d39d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92cfcd757f9cee25d5ba4375de986d26b123c0a892ebe6ba25509acc6227cba3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b960b63beef0cde54763552d779b2cd981c2a474766ed69e0a2da51775bc216b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970eab4f5359aecda3375d8e1dee6545e5b8fd3ed9ebbe3e511b3d0be9218aa7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6948600f4627cd62855d03ff3234112015ad0b8e183f1bc0e091b0093b3d97a4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    endpoint_name: builtins.str,
    index_type: builtins.str,
    name: builtins.str,
    primary_key: builtins.str,
    delta_sync_index_spec: typing.Optional[typing.Union[VectorSearchIndexDeltaSyncIndexSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    direct_access_index_spec: typing.Optional[typing.Union[VectorSearchIndexDirectAccessIndexSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VectorSearchIndexTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__022daafaad134b4e3ca64c58d7359b2b6603ccfa3105580f61d74d77ff0a1c44(
    *,
    embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    embedding_writeback_table: typing.Optional[builtins.str] = None,
    pipeline_type: typing.Optional[builtins.str] = None,
    source_table: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc196a6bad19cd59dcc12865e40d6977a038464cd63dc5771acea84ceac59e3(
    *,
    embedding_model_endpoint_name: typing.Optional[builtins.str] = None,
    model_endpoint_name_for_query: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bfcccaf0a7a8869597bc041cdcf634ce8301413b30056dbd3b638334478b909(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__071c6f67b2bd48e7339212b7b8b7b50492aff07f54fad9836a74588fe9440de8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e607529f9b6bd1a033fb8936ddf4cfe3e7324ae97379fc15ae0c60524c0f2f03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af0d138c20907c18891de046ee71a543477b63691e0b236bb705983a06b2d6f5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5887b2fbe29f2fe97bf6c37afecf7b58f72e9ada6f2670281fa76bb971ed4969(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc02e10c6f63088f43c6d948beea13a6a27876a19f8029c25e151c9467f19a5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2af0293b8e76cdd5c2513e551ff0a809acab2ad17ce460ab1da4648985be4a0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66da0438965a52c0e279430cdb4875df3559d427ec153d3bf7b45c08adf00d05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d420c2f332dfeba08149bbfd72dc504583fe4af55f12662fae5429348f88ad7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11239aad44eb38667bec58a54bd4d44c271211d32c42ce6f5e8b645b6022d487(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ed2677a1c5e81c5aa3da8953cee7f07ec1996d721d50146f2095d727b4ac28(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfca5f52c24720a8eaa0e5eb000460d37e10cbd5001763609febbd35c1c7666a(
    *,
    embedding_dimension: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f0e4ef55669c181d2c9b1731aeff47cc12b3d54874ccd135a7b518d928c90fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e39513701d797e887890e21ca4d22bbbe29140f9f4aee36b6d86c74b03071a1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ade831f62f672d2e9fe41bd79ab6a161ca4e22695656ee1533a02cfe5e4819(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23246593f2557c8110d30bcd693cf78dcab3e7aa143baaedc1828e2d83568d79(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf304163263c8d9c898c451ab6c520cc0110cafe1223e6049c05c40ef1c0fcf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f12b53d4f453005d76b749b5298c4c12c423823c346a067ee421eda081c4412e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eba59fd5207d4a95158b28d78a6978c00ce7631758cecbb0010058d42e6e151(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69466ae66649b1f7596d5e76d43eedc196daf78ca9eb722f1037e6b1d1ba7a5c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3cf8628eea5382792b440308a454cb9e18069fb92088dd2fa6473b551db9255(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d09be432791edd8791b7beaca2d027138d6dea0d14f600ea4897981bdbb737bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d42372c6682813f7cdc453673793df9270b15d3ba717ac25b63fef33fe1402f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b8f3d3f77cffca224b83947da1ce9524cfaefd7ef6a11d19a36b530aed3a79(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__992ad469a204083eff4e8f8c9f26565018a1849c69a5a2fd3cfa47e6c68a2e0c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDeltaSyncIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60db1f3d98763481b73841cc14c2656482e3855f9804ba41c40214f05f9312a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d2451938ee58ed05825fcc1a85e795cd064d76c494f0bf246769f392f17da7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c24b9cf078f5a639560c06c8b1c457f05c325bd5fc35a2ca2e023fbe787bae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a28fafeda0bdfbe976c6c93c44fe4b9cf43c53a4c1b50a73fa864669ff3380(
    value: typing.Optional[VectorSearchIndexDeltaSyncIndexSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c32d6e9f6680a2641c1416371b599d1f83300cbc488852ca0fd4604c2460148(
    *,
    embedding_source_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    embedding_vector_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    schema_json: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0409f064172e233053af15ac516c3a6accc6cf0c5d64aee774859d39494f8419(
    *,
    embedding_model_endpoint_name: typing.Optional[builtins.str] = None,
    model_endpoint_name_for_query: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0915fa5419f5fca105b84fee74fa653a3edae4a193c52e7c271f31fc7e159a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef26a729c2e8e0613f848934cd127da4682612e9115c41fad8e5e459e37be4ae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eddcbcc686ef75633687f1390b185dbf3851044760862807f84b2dea8eb9508(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffa5664c78991da340294f46a1f770cf3febecbbf2414e7adf573cf2e97a5d5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24958ab483d540e1d55753735d3c2b19fb1435ec94eeeb8cd3456779048543f7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__513e274fb2dace55da22d15124f8c17cf489aefa4f6528546e76321244d78635(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27e0274c839f9ad99491e55028732f0bf78be9bb7337ebd5e765497e55e4073(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433829bb84799fc571d8f8f7bceec0258624872194dcfaba387bb0ba975ff72a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1349a202214dcd0143ba13aeae08a7b6e64b6f3cca71d108f72392dc56f277(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af8931d3f6df07702d3dd0d1c321bb8b95d8e2077ee7a0d0df1fbe9b4f1964b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dee08e5f33083e985bec81ff4d4b6bfe0e4db2a6a1397662e9fb8468c6ade92c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5e5ea5ac7e187729377f403c1c2ec6c5f9ceaca31be22e8727b0f329b2608a0(
    *,
    embedding_dimension: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba08be7fc4f4c953fdc7a5338020ad5a8bb4a8327d551d700a0ad88ff54f4f64(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d060f9e4542035fbdc424346d11ba25f784d7fa53283428ec4beef12d3bfb0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0158fbce68b5aee24179768ac6785ef5d3180ef1744409baab7f7bce857723c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee7b1052b41563f7d1799f4d4e37e5c45967d868111ce40f5e0051789e6da05(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fadf2a672c6d67b6aae6033197bf759e306c89d5efdcdcfcb2ce6396baac825(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47e2548d59a30f576bf00e4deedf3948d12339f902341f7342ed3fffe3c7c895(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2778cd602e2370e14a17cb97e1bbe75560d8837c5cc0c13f0e67bd9099879d5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568fcb1bb49f93fde783dc5d8c60bb41baab04fed58fa496e9e3645401ba949c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42e4e6a5d7fb40d15848f915adfe1809376180d84ce3af5aacf6a56d97c43620(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f37bca937d18c6d3c81772c7adaddc337972dcc65cd6ee32ee2f5e4b6c2dd7e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f8c5ad5b634127aa7c7e71e18e9ec1d8ce468e2fe1dbec2850be9fc1b821d07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04e70b4afdaeb076f13cbb7e378db04d1808aaca658bf77c971a4c126ae6f4ec(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingSourceColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d2ceb0b30dbd1d89bb9a4cee5de650ceded34c681d09525e3054b7903653f21(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VectorSearchIndexDirectAccessIndexSpecEmbeddingVectorColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955ab7e7bb2acd047dd6ce712c6bebdae7fd890baccd96ba477ff44f0ca7ae0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e986bd8eacf4780cd27a028ff1d7d8a0dab2ab87c1d834c692feff00d6ffd231(
    value: typing.Optional[VectorSearchIndexDirectAccessIndexSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__978988ace88a078f64f255cf8c66781775dfa9709cdce9e3df5b47f51078730f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9eb45fc8cd280c747c115f8700b035f263d46a6a8a8324c4029731e50920f1d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c8665c29f1712488101bc91858697dfcc89c9cf409d53f20787c491f5ed74eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd3fe1cd5e16f8c2320d12f9cf2a0272dd310335ff475ba3c64ae44ec1f395d6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57010a49fa5e1ba72ded99efb83c73999b605085792b73dc9ff02a2b2a7b03bb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23b7df296d1526bca88367d72b2821f03049e6ac81770d839c9933f5c5bbd4d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffe5db9c0390095125a571817ddf2c5c25ddca800c3a7a7ee5a5a009d14f27a9(
    value: typing.Optional[VectorSearchIndexStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__283520b3fe14bfaddb20c7ffcbb6dfbf7e9505286dc01a987123452ebee5bf38(
    *,
    create: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55318db47e587306f3e5486cd2730a92104933a4c01ff4d847aa98a384e04e14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ff0aa6c998f9c065bbf095078eccc8ecddac5937f52a9cb02fc6a351fdf5ae2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a6440b4936a0cd3c17ce447399610d5bbd1f9d37180f3ddec2fba1cd1236c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VectorSearchIndexTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
