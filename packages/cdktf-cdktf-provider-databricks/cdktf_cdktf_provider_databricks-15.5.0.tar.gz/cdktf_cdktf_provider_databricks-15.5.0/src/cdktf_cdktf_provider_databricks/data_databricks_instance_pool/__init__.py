r'''
# `data_databricks_instance_pool`

Refer to the Terraform Registry for docs: [`data_databricks_instance_pool`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool).
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


class DataDatabricksInstancePool(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePool",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool databricks_instance_pool}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        pool_info: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool databricks_instance_pool} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#name DataDatabricksInstancePool#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#id DataDatabricksInstancePool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pool_info: pool_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pool_info DataDatabricksInstancePool#pool_info}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06c9b25c5147765a557f1f0ad8681343ca321a784ea18d6a49dd362ef828c084)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksInstancePoolConfig(
            name=name,
            id=id,
            pool_info=pool_info,
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
        '''Generates CDKTF code for importing a DataDatabricksInstancePool resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksInstancePool to import.
        :param import_from_id: The id of the existing DataDatabricksInstancePool that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksInstancePool to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5099b803ecfad924f1464bb26bff495b842e304b5e19ed1daa85d36e86686e9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putPoolInfo")
    def put_pool_info(
        self,
        *,
        idle_instance_autotermination_minutes: jsii.Number,
        instance_pool_name: builtins.str,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disk_spec: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoDiskSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_pool_fleet_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_idle_instances: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        state: typing.Optional[builtins.str] = None,
        stats: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoStats", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param idle_instance_autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_instance_autotermination_minutes DataDatabricksInstancePool#idle_instance_autotermination_minutes}.
        :param instance_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_name DataDatabricksInstancePool#instance_pool_name}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#aws_attributes DataDatabricksInstancePool#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_attributes DataDatabricksInstancePool#azure_attributes}
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#custom_tags DataDatabricksInstancePool#custom_tags}.
        :param default_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#default_tags DataDatabricksInstancePool#default_tags}.
        :param disk_spec: disk_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_spec DataDatabricksInstancePool#disk_spec}
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#enable_elastic_disk DataDatabricksInstancePool#enable_elastic_disk}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_attributes DataDatabricksInstancePool#gcp_attributes}
        :param instance_pool_fleet_attributes: instance_pool_fleet_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_fleet_attributes DataDatabricksInstancePool#instance_pool_fleet_attributes}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_id DataDatabricksInstancePool#instance_pool_id}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#max_capacity DataDatabricksInstancePool#max_capacity}.
        :param min_idle_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#min_idle_instances DataDatabricksInstancePool#min_idle_instances}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#node_type_id DataDatabricksInstancePool#node_type_id}.
        :param preloaded_docker_image: preloaded_docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_docker_image DataDatabricksInstancePool#preloaded_docker_image}
        :param preloaded_spark_versions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_spark_versions DataDatabricksInstancePool#preloaded_spark_versions}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#state DataDatabricksInstancePool#state}.
        :param stats: stats block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#stats DataDatabricksInstancePool#stats}
        '''
        value = DataDatabricksInstancePoolPoolInfo(
            idle_instance_autotermination_minutes=idle_instance_autotermination_minutes,
            instance_pool_name=instance_pool_name,
            aws_attributes=aws_attributes,
            azure_attributes=azure_attributes,
            custom_tags=custom_tags,
            default_tags=default_tags,
            disk_spec=disk_spec,
            enable_elastic_disk=enable_elastic_disk,
            gcp_attributes=gcp_attributes,
            instance_pool_fleet_attributes=instance_pool_fleet_attributes,
            instance_pool_id=instance_pool_id,
            max_capacity=max_capacity,
            min_idle_instances=min_idle_instances,
            node_type_id=node_type_id,
            preloaded_docker_image=preloaded_docker_image,
            preloaded_spark_versions=preloaded_spark_versions,
            state=state,
            stats=stats,
        )

        return typing.cast(None, jsii.invoke(self, "putPoolInfo", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPoolInfo")
    def reset_pool_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPoolInfo", []))

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
    @jsii.member(jsii_name="poolInfo")
    def pool_info(self) -> "DataDatabricksInstancePoolPoolInfoOutputReference":
        return typing.cast("DataDatabricksInstancePoolPoolInfoOutputReference", jsii.get(self, "poolInfo"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="poolInfoInput")
    def pool_info_input(self) -> typing.Optional["DataDatabricksInstancePoolPoolInfo"]:
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfo"], jsii.get(self, "poolInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd0b9f094868163cd882a994ea3a5ad643453c6b0f2071a56b0a6160eb78e544)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__207197444fdbde2682499dc73f7eb9ea3cd24958c32fe4b458f5b04f5c17e147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolConfig",
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
        "id": "id",
        "pool_info": "poolInfo",
    },
)
class DataDatabricksInstancePoolConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        pool_info: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfo", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#name DataDatabricksInstancePool#name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#id DataDatabricksInstancePool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pool_info: pool_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pool_info DataDatabricksInstancePool#pool_info}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(pool_info, dict):
            pool_info = DataDatabricksInstancePoolPoolInfo(**pool_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4886511e6d711662977562a730a725479a50b233e19b52f8e429acad645297ba)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument pool_info", value=pool_info, expected_type=type_hints["pool_info"])
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
        if id is not None:
            self._values["id"] = id
        if pool_info is not None:
            self._values["pool_info"] = pool_info

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#name DataDatabricksInstancePool#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#id DataDatabricksInstancePool#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pool_info(self) -> typing.Optional["DataDatabricksInstancePoolPoolInfo"]:
        '''pool_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pool_info DataDatabricksInstancePool#pool_info}
        '''
        result = self._values.get("pool_info")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfo",
    jsii_struct_bases=[],
    name_mapping={
        "idle_instance_autotermination_minutes": "idleInstanceAutoterminationMinutes",
        "instance_pool_name": "instancePoolName",
        "aws_attributes": "awsAttributes",
        "azure_attributes": "azureAttributes",
        "custom_tags": "customTags",
        "default_tags": "defaultTags",
        "disk_spec": "diskSpec",
        "enable_elastic_disk": "enableElasticDisk",
        "gcp_attributes": "gcpAttributes",
        "instance_pool_fleet_attributes": "instancePoolFleetAttributes",
        "instance_pool_id": "instancePoolId",
        "max_capacity": "maxCapacity",
        "min_idle_instances": "minIdleInstances",
        "node_type_id": "nodeTypeId",
        "preloaded_docker_image": "preloadedDockerImage",
        "preloaded_spark_versions": "preloadedSparkVersions",
        "state": "state",
        "stats": "stats",
    },
)
class DataDatabricksInstancePoolPoolInfo:
    def __init__(
        self,
        *,
        idle_instance_autotermination_minutes: jsii.Number,
        instance_pool_name: builtins.str,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disk_spec: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoDiskSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_pool_fleet_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_idle_instances: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        state: typing.Optional[builtins.str] = None,
        stats: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoStats", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param idle_instance_autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_instance_autotermination_minutes DataDatabricksInstancePool#idle_instance_autotermination_minutes}.
        :param instance_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_name DataDatabricksInstancePool#instance_pool_name}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#aws_attributes DataDatabricksInstancePool#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_attributes DataDatabricksInstancePool#azure_attributes}
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#custom_tags DataDatabricksInstancePool#custom_tags}.
        :param default_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#default_tags DataDatabricksInstancePool#default_tags}.
        :param disk_spec: disk_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_spec DataDatabricksInstancePool#disk_spec}
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#enable_elastic_disk DataDatabricksInstancePool#enable_elastic_disk}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_attributes DataDatabricksInstancePool#gcp_attributes}
        :param instance_pool_fleet_attributes: instance_pool_fleet_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_fleet_attributes DataDatabricksInstancePool#instance_pool_fleet_attributes}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_id DataDatabricksInstancePool#instance_pool_id}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#max_capacity DataDatabricksInstancePool#max_capacity}.
        :param min_idle_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#min_idle_instances DataDatabricksInstancePool#min_idle_instances}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#node_type_id DataDatabricksInstancePool#node_type_id}.
        :param preloaded_docker_image: preloaded_docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_docker_image DataDatabricksInstancePool#preloaded_docker_image}
        :param preloaded_spark_versions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_spark_versions DataDatabricksInstancePool#preloaded_spark_versions}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#state DataDatabricksInstancePool#state}.
        :param stats: stats block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#stats DataDatabricksInstancePool#stats}
        '''
        if isinstance(aws_attributes, dict):
            aws_attributes = DataDatabricksInstancePoolPoolInfoAwsAttributes(**aws_attributes)
        if isinstance(azure_attributes, dict):
            azure_attributes = DataDatabricksInstancePoolPoolInfoAzureAttributes(**azure_attributes)
        if isinstance(disk_spec, dict):
            disk_spec = DataDatabricksInstancePoolPoolInfoDiskSpec(**disk_spec)
        if isinstance(gcp_attributes, dict):
            gcp_attributes = DataDatabricksInstancePoolPoolInfoGcpAttributes(**gcp_attributes)
        if isinstance(stats, dict):
            stats = DataDatabricksInstancePoolPoolInfoStats(**stats)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a04c76888462ad56259b8a7d77e6b5d968bf8036432aae0a5812523ba89ab858)
            check_type(argname="argument idle_instance_autotermination_minutes", value=idle_instance_autotermination_minutes, expected_type=type_hints["idle_instance_autotermination_minutes"])
            check_type(argname="argument instance_pool_name", value=instance_pool_name, expected_type=type_hints["instance_pool_name"])
            check_type(argname="argument aws_attributes", value=aws_attributes, expected_type=type_hints["aws_attributes"])
            check_type(argname="argument azure_attributes", value=azure_attributes, expected_type=type_hints["azure_attributes"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument default_tags", value=default_tags, expected_type=type_hints["default_tags"])
            check_type(argname="argument disk_spec", value=disk_spec, expected_type=type_hints["disk_spec"])
            check_type(argname="argument enable_elastic_disk", value=enable_elastic_disk, expected_type=type_hints["enable_elastic_disk"])
            check_type(argname="argument gcp_attributes", value=gcp_attributes, expected_type=type_hints["gcp_attributes"])
            check_type(argname="argument instance_pool_fleet_attributes", value=instance_pool_fleet_attributes, expected_type=type_hints["instance_pool_fleet_attributes"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_idle_instances", value=min_idle_instances, expected_type=type_hints["min_idle_instances"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument preloaded_docker_image", value=preloaded_docker_image, expected_type=type_hints["preloaded_docker_image"])
            check_type(argname="argument preloaded_spark_versions", value=preloaded_spark_versions, expected_type=type_hints["preloaded_spark_versions"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument stats", value=stats, expected_type=type_hints["stats"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "idle_instance_autotermination_minutes": idle_instance_autotermination_minutes,
            "instance_pool_name": instance_pool_name,
        }
        if aws_attributes is not None:
            self._values["aws_attributes"] = aws_attributes
        if azure_attributes is not None:
            self._values["azure_attributes"] = azure_attributes
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if default_tags is not None:
            self._values["default_tags"] = default_tags
        if disk_spec is not None:
            self._values["disk_spec"] = disk_spec
        if enable_elastic_disk is not None:
            self._values["enable_elastic_disk"] = enable_elastic_disk
        if gcp_attributes is not None:
            self._values["gcp_attributes"] = gcp_attributes
        if instance_pool_fleet_attributes is not None:
            self._values["instance_pool_fleet_attributes"] = instance_pool_fleet_attributes
        if instance_pool_id is not None:
            self._values["instance_pool_id"] = instance_pool_id
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_idle_instances is not None:
            self._values["min_idle_instances"] = min_idle_instances
        if node_type_id is not None:
            self._values["node_type_id"] = node_type_id
        if preloaded_docker_image is not None:
            self._values["preloaded_docker_image"] = preloaded_docker_image
        if preloaded_spark_versions is not None:
            self._values["preloaded_spark_versions"] = preloaded_spark_versions
        if state is not None:
            self._values["state"] = state
        if stats is not None:
            self._values["stats"] = stats

    @builtins.property
    def idle_instance_autotermination_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_instance_autotermination_minutes DataDatabricksInstancePool#idle_instance_autotermination_minutes}.'''
        result = self._values.get("idle_instance_autotermination_minutes")
        assert result is not None, "Required property 'idle_instance_autotermination_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def instance_pool_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_name DataDatabricksInstancePool#instance_pool_name}.'''
        result = self._values.get("instance_pool_name")
        assert result is not None, "Required property 'instance_pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_attributes(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoAwsAttributes"]:
        '''aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#aws_attributes DataDatabricksInstancePool#aws_attributes}
        '''
        result = self._values.get("aws_attributes")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoAwsAttributes"], result)

    @builtins.property
    def azure_attributes(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoAzureAttributes"]:
        '''azure_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_attributes DataDatabricksInstancePool#azure_attributes}
        '''
        result = self._values.get("azure_attributes")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoAzureAttributes"], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#custom_tags DataDatabricksInstancePool#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def default_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#default_tags DataDatabricksInstancePool#default_tags}.'''
        result = self._values.get("default_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def disk_spec(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoDiskSpec"]:
        '''disk_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_spec DataDatabricksInstancePool#disk_spec}
        '''
        result = self._values.get("disk_spec")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoDiskSpec"], result)

    @builtins.property
    def enable_elastic_disk(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#enable_elastic_disk DataDatabricksInstancePool#enable_elastic_disk}.'''
        result = self._values.get("enable_elastic_disk")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gcp_attributes(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoGcpAttributes"]:
        '''gcp_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_attributes DataDatabricksInstancePool#gcp_attributes}
        '''
        result = self._values.get("gcp_attributes")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoGcpAttributes"], result)

    @builtins.property
    def instance_pool_fleet_attributes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes"]]]:
        '''instance_pool_fleet_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_fleet_attributes DataDatabricksInstancePool#instance_pool_fleet_attributes}
        '''
        result = self._values.get("instance_pool_fleet_attributes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes"]]], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pool_id DataDatabricksInstancePool#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#max_capacity DataDatabricksInstancePool#max_capacity}.'''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_idle_instances(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#min_idle_instances DataDatabricksInstancePool#min_idle_instances}.'''
        result = self._values.get("min_idle_instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#node_type_id DataDatabricksInstancePool#node_type_id}.'''
        result = self._values.get("node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preloaded_docker_image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage"]]]:
        '''preloaded_docker_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_docker_image DataDatabricksInstancePool#preloaded_docker_image}
        '''
        result = self._values.get("preloaded_docker_image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage"]]], result)

    @builtins.property
    def preloaded_spark_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#preloaded_spark_versions DataDatabricksInstancePool#preloaded_spark_versions}.'''
        result = self._values.get("preloaded_spark_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#state DataDatabricksInstancePool#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stats(self) -> typing.Optional["DataDatabricksInstancePoolPoolInfoStats"]:
        '''stats block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#stats DataDatabricksInstancePool#stats}
        '''
        result = self._values.get("stats")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoStats"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "spot_bid_price_percent": "spotBidPricePercent",
        "zone_id": "zoneId",
    },
)
class DataDatabricksInstancePoolPoolInfoAwsAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_price_percent DataDatabricksInstancePool#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc6dd9a31b27335c60098d5d62a5fc919b8ba52f3008ccc0dfb76a2d200804c9)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument spot_bid_price_percent", value=spot_bid_price_percent, expected_type=type_hints["spot_bid_price_percent"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if spot_bid_price_percent is not None:
            self._values["spot_bid_price_percent"] = spot_bid_price_percent
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_price_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_price_percent DataDatabricksInstancePool#spot_bid_price_percent}.'''
        result = self._values.get("spot_bid_price_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc23a07bd96c35abcf9f9aa10f45916745df9a27e82f08ab4f2c25bc080d799f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetSpotBidPricePercent")
    def reset_spot_bid_price_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidPricePercent", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercentInput")
    def spot_bid_price_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotBidPricePercentInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="availability")
    def availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availability"))

    @availability.setter
    def availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ea68c10754aba3db42806a82d5a4037ab9e5a5252298077e2dd45fb23bc427c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercent")
    def spot_bid_price_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidPricePercent"))

    @spot_bid_price_percent.setter
    def spot_bid_price_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01829f38cb2ac8e2e4ebdd0334f4179e8be7e2980e6ba423a559cc11664afd0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidPricePercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b38e2cac5e9ce6e003ec79c4c1ab0231124a4e88feac5ab06842fb23b21e5dfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13afe210d5408b9a52f5b7e9c90afbdf55bf126f71705cb88d18be7fb7146e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoAzureAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "spot_bid_max_price": "spotBidMaxPrice",
    },
)
class DataDatabricksInstancePoolPoolInfoAzureAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_max_price DataDatabricksInstancePool#spot_bid_max_price}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ce15ae9944a723a6ebe2117c618de2266f73f17376e5b2f21928b7c5573bd93)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument spot_bid_max_price", value=spot_bid_max_price, expected_type=type_hints["spot_bid_max_price"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if spot_bid_max_price is not None:
            self._values["spot_bid_max_price"] = spot_bid_max_price

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_max_price(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_max_price DataDatabricksInstancePool#spot_bid_max_price}.'''
        result = self._values.get("spot_bid_max_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoAzureAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoAzureAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoAzureAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c5ff60be5ca782c2ce865b5b78658cea89cea156d89929688d0468929daf05f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetSpotBidMaxPrice")
    def reset_spot_bid_max_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidMaxPrice", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPriceInput")
    def spot_bid_max_price_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotBidMaxPriceInput"))

    @builtins.property
    @jsii.member(jsii_name="availability")
    def availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availability"))

    @availability.setter
    def availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2daf2588b0c622770e8179a7c6329b7e5205278eb6ceae39d747c30705bd40fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPrice")
    def spot_bid_max_price(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidMaxPrice"))

    @spot_bid_max_price.setter
    def spot_bid_max_price(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0781c6198387d55928dd37ccf1e761a279c88019d4a01e58f719dd742e0b9246)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidMaxPrice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae08292ffd33227158e946eab2c9bb47a289d6afbb2951b58d64c4c6ddc45e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoDiskSpec",
    jsii_struct_bases=[],
    name_mapping={
        "disk_count": "diskCount",
        "disk_size": "diskSize",
        "disk_type": "diskType",
    },
)
class DataDatabricksInstancePoolPoolInfoDiskSpec:
    def __init__(
        self,
        *,
        disk_count: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        disk_type: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoDiskSpecDiskType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param disk_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_count DataDatabricksInstancePool#disk_count}.
        :param disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_size DataDatabricksInstancePool#disk_size}.
        :param disk_type: disk_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_type DataDatabricksInstancePool#disk_type}
        '''
        if isinstance(disk_type, dict):
            disk_type = DataDatabricksInstancePoolPoolInfoDiskSpecDiskType(**disk_type)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9c9ad16008a2caabcf33de7aa2f8e47ee23cbf0d995987800f2e8a8b161b754)
            check_type(argname="argument disk_count", value=disk_count, expected_type=type_hints["disk_count"])
            check_type(argname="argument disk_size", value=disk_size, expected_type=type_hints["disk_size"])
            check_type(argname="argument disk_type", value=disk_type, expected_type=type_hints["disk_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disk_count is not None:
            self._values["disk_count"] = disk_count
        if disk_size is not None:
            self._values["disk_size"] = disk_size
        if disk_type is not None:
            self._values["disk_type"] = disk_type

    @builtins.property
    def disk_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_count DataDatabricksInstancePool#disk_count}.'''
        result = self._values.get("disk_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_size DataDatabricksInstancePool#disk_size}.'''
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_type(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoDiskSpecDiskType"]:
        '''disk_type block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_type DataDatabricksInstancePool#disk_type}
        '''
        result = self._values.get("disk_type")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoDiskSpecDiskType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoDiskSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoDiskSpecDiskType",
    jsii_struct_bases=[],
    name_mapping={
        "azure_disk_volume_type": "azureDiskVolumeType",
        "ebs_volume_type": "ebsVolumeType",
    },
)
class DataDatabricksInstancePoolPoolInfoDiskSpecDiskType:
    def __init__(
        self,
        *,
        azure_disk_volume_type: typing.Optional[builtins.str] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param azure_disk_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_disk_volume_type DataDatabricksInstancePool#azure_disk_volume_type}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#ebs_volume_type DataDatabricksInstancePool#ebs_volume_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89478803c566b8c2597263e5eb6bc110fc0e9319a8dfc96817f410c0ececef70)
            check_type(argname="argument azure_disk_volume_type", value=azure_disk_volume_type, expected_type=type_hints["azure_disk_volume_type"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if azure_disk_volume_type is not None:
            self._values["azure_disk_volume_type"] = azure_disk_volume_type
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type

    @builtins.property
    def azure_disk_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_disk_volume_type DataDatabricksInstancePool#azure_disk_volume_type}.'''
        result = self._values.get("azure_disk_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#ebs_volume_type DataDatabricksInstancePool#ebs_volume_type}.'''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoDiskSpecDiskType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoDiskSpecDiskTypeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoDiskSpecDiskTypeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7d4aeb00b919fc8762e5dc6dbd072d7f3338ce1fa38c2d8fcd6027ffcd62d78)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAzureDiskVolumeType")
    def reset_azure_disk_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureDiskVolumeType", []))

    @jsii.member(jsii_name="resetEbsVolumeType")
    def reset_ebs_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeType", []))

    @builtins.property
    @jsii.member(jsii_name="azureDiskVolumeTypeInput")
    def azure_disk_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureDiskVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeTypeInput")
    def ebs_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ebsVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="azureDiskVolumeType")
    def azure_disk_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureDiskVolumeType"))

    @azure_disk_volume_type.setter
    def azure_disk_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74aeffe39a0a211c1635d5d2aa4513cb841f2dd6b47ea265055f30eab73ea44f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureDiskVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeType")
    def ebs_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ebsVolumeType"))

    @ebs_volume_type.setter
    def ebs_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8079e482ec956c6fe17a2203b90a02f64b671e0844c2f07f2a9c107bffaabbab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4202000dd5f4367d2c6d5827ee2d92472b8fe989e580bb726cb16f8d3b63b4aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoDiskSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoDiskSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5764fd1b4760e200952757288e859c0d6dce4df3bb3701af75472ac93aad00c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDiskType")
    def put_disk_type(
        self,
        *,
        azure_disk_volume_type: typing.Optional[builtins.str] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param azure_disk_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#azure_disk_volume_type DataDatabricksInstancePool#azure_disk_volume_type}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#ebs_volume_type DataDatabricksInstancePool#ebs_volume_type}.
        '''
        value = DataDatabricksInstancePoolPoolInfoDiskSpecDiskType(
            azure_disk_volume_type=azure_disk_volume_type,
            ebs_volume_type=ebs_volume_type,
        )

        return typing.cast(None, jsii.invoke(self, "putDiskType", [value]))

    @jsii.member(jsii_name="resetDiskCount")
    def reset_disk_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskCount", []))

    @jsii.member(jsii_name="resetDiskSize")
    def reset_disk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSize", []))

    @jsii.member(jsii_name="resetDiskType")
    def reset_disk_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskType", []))

    @builtins.property
    @jsii.member(jsii_name="diskType")
    def disk_type(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoDiskSpecDiskTypeOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoDiskSpecDiskTypeOutputReference, jsii.get(self, "diskType"))

    @builtins.property
    @jsii.member(jsii_name="diskCountInput")
    def disk_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "diskCountInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeInput")
    def disk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "diskSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTypeInput")
    def disk_type_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType], jsii.get(self, "diskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="diskCount")
    def disk_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskCount"))

    @disk_count.setter
    def disk_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a1bc483560b5995d533b17f9dc9f8e65e9b7dbe7a652a17ae878731efaa6d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskSize")
    def disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskSize"))

    @disk_size.setter
    def disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cc6573caa0f7027ac5da5cb8b51c68a340161035214fb9486512c35ed680456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90c32a9751ff77860ab075d6619c8aab17e66639fbd49e977926046adf3f0a43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoGcpAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "gcp_availability": "gcpAvailability",
        "local_ssd_count": "localSsdCount",
        "zone_id": "zoneId",
    },
)
class DataDatabricksInstancePoolPoolInfoGcpAttributes:
    def __init__(
        self,
        *,
        gcp_availability: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param gcp_availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_availability DataDatabricksInstancePool#gcp_availability}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#local_ssd_count DataDatabricksInstancePool#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac073e583f1e0f1984dc21b57638a368786cd5091f95f629f9d973e2bfaee437)
            check_type(argname="argument gcp_availability", value=gcp_availability, expected_type=type_hints["gcp_availability"])
            check_type(argname="argument local_ssd_count", value=local_ssd_count, expected_type=type_hints["local_ssd_count"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if gcp_availability is not None:
            self._values["gcp_availability"] = gcp_availability
        if local_ssd_count is not None:
            self._values["local_ssd_count"] = local_ssd_count
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def gcp_availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_availability DataDatabricksInstancePool#gcp_availability}.'''
        result = self._values.get("gcp_availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#local_ssd_count DataDatabricksInstancePool#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoGcpAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoGcpAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoGcpAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__623ba4b8a406ea7fd0d14ac3a35acd71591031a67883db2b68ae5c0cdc0337d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGcpAvailability")
    def reset_gcp_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAvailability", []))

    @jsii.member(jsii_name="resetLocalSsdCount")
    def reset_local_ssd_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSsdCount", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="gcpAvailabilityInput")
    def gcp_availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpAvailabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="localSsdCountInput")
    def local_ssd_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localSsdCountInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAvailability")
    def gcp_availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpAvailability"))

    @gcp_availability.setter
    def gcp_availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e47eb9bdd5904a0aeadefe9de34e15b32ceec8c979023aed05064dfefcfacde3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpAvailability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dd63e60eb25fbd6b083680a955b284f9a3d89a76cec03cb49b32a8743cee804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29125e44588c94ead02f9474c845bdc0e75491aca698842eee35af144ab0aa6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c1de4aa407300724cd47fa1c0d694eac8ae18b96592c42412eabfeaacd79d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "launch_template_override": "launchTemplateOverride",
        "fleet_on_demand_option": "fleetOnDemandOption",
        "fleet_spot_option": "fleetSpotOption",
    },
)
class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes:
    def __init__(
        self,
        *,
        launch_template_override: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride", typing.Dict[builtins.str, typing.Any]]]],
        fleet_on_demand_option: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption", typing.Dict[builtins.str, typing.Any]]] = None,
        fleet_spot_option: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param launch_template_override: launch_template_override block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#launch_template_override DataDatabricksInstancePool#launch_template_override}
        :param fleet_on_demand_option: fleet_on_demand_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#fleet_on_demand_option DataDatabricksInstancePool#fleet_on_demand_option}
        :param fleet_spot_option: fleet_spot_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#fleet_spot_option DataDatabricksInstancePool#fleet_spot_option}
        '''
        if isinstance(fleet_on_demand_option, dict):
            fleet_on_demand_option = DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption(**fleet_on_demand_option)
        if isinstance(fleet_spot_option, dict):
            fleet_spot_option = DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption(**fleet_spot_option)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__004f263e57574d172f155674ed274dd16b2f777275665638edf78fb76d2ff9ac)
            check_type(argname="argument launch_template_override", value=launch_template_override, expected_type=type_hints["launch_template_override"])
            check_type(argname="argument fleet_on_demand_option", value=fleet_on_demand_option, expected_type=type_hints["fleet_on_demand_option"])
            check_type(argname="argument fleet_spot_option", value=fleet_spot_option, expected_type=type_hints["fleet_spot_option"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "launch_template_override": launch_template_override,
        }
        if fleet_on_demand_option is not None:
            self._values["fleet_on_demand_option"] = fleet_on_demand_option
        if fleet_spot_option is not None:
            self._values["fleet_spot_option"] = fleet_spot_option

    @builtins.property
    def launch_template_override(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride"]]:
        '''launch_template_override block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#launch_template_override DataDatabricksInstancePool#launch_template_override}
        '''
        result = self._values.get("launch_template_override")
        assert result is not None, "Required property 'launch_template_override' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride"]], result)

    @builtins.property
    def fleet_on_demand_option(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption"]:
        '''fleet_on_demand_option block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#fleet_on_demand_option DataDatabricksInstancePool#fleet_on_demand_option}
        '''
        result = self._values.get("fleet_on_demand_option")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption"], result)

    @builtins.property
    def fleet_spot_option(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption"]:
        '''fleet_spot_option block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#fleet_spot_option DataDatabricksInstancePool#fleet_spot_option}
        '''
        result = self._values.get("fleet_spot_option")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "instance_pools_to_use_count": "instancePoolsToUseCount",
    },
)
class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc5cd545b560327bd77242ca1347c939d42e53f51f380694fc35481ed825e8a)
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument instance_pools_to_use_count", value=instance_pools_to_use_count, expected_type=type_hints["instance_pools_to_use_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }
        if instance_pools_to_use_count is not None:
            self._values["instance_pools_to_use_count"] = instance_pools_to_use_count

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_pools_to_use_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.'''
        result = self._values.get("instance_pools_to_use_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9be92fb47249dbebf2575e73671c962f3ac4d3acf91f6af48de94e03db5c0c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInstancePoolsToUseCount")
    def reset_instance_pools_to_use_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolsToUseCount", []))

    @builtins.property
    @jsii.member(jsii_name="allocationStrategyInput")
    def allocation_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allocationStrategyInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCountInput")
    def instance_pools_to_use_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instancePoolsToUseCountInput"))

    @builtins.property
    @jsii.member(jsii_name="allocationStrategy")
    def allocation_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allocationStrategy"))

    @allocation_strategy.setter
    def allocation_strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1d659ffb15cb2841a05b5ee1a104131e459aa01cf2edbc7ce9ece5332f4033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allocationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCount")
    def instance_pools_to_use_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instancePoolsToUseCount"))

    @instance_pools_to_use_count.setter
    def instance_pools_to_use_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0707798a3a22168c8d36e94464aee6d730a73b82e2cd9d592022492c51445445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolsToUseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ff022c892c40ef1fc055fed1417dc87e28109b61636f535a9a89b5ac979e799)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "instance_pools_to_use_count": "instancePoolsToUseCount",
    },
)
class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ef06fa2cbe82b736b782367c2f507f26c1970e10984a756506833b617545c01)
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument instance_pools_to_use_count", value=instance_pools_to_use_count, expected_type=type_hints["instance_pools_to_use_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }
        if instance_pools_to_use_count is not None:
            self._values["instance_pools_to_use_count"] = instance_pools_to_use_count

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_pools_to_use_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.'''
        result = self._values.get("instance_pools_to_use_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d43876023a55304b3cb05bb6281de649457886cdb632e628569b1d24b036528)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInstancePoolsToUseCount")
    def reset_instance_pools_to_use_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolsToUseCount", []))

    @builtins.property
    @jsii.member(jsii_name="allocationStrategyInput")
    def allocation_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allocationStrategyInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCountInput")
    def instance_pools_to_use_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instancePoolsToUseCountInput"))

    @builtins.property
    @jsii.member(jsii_name="allocationStrategy")
    def allocation_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allocationStrategy"))

    @allocation_strategy.setter
    def allocation_strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4b0bc7a715a18b0c07224451e7c9014f908311ba421bdc87a6cd740abcdaa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allocationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCount")
    def instance_pools_to_use_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instancePoolsToUseCount"))

    @instance_pools_to_use_count.setter
    def instance_pools_to_use_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f4d9fe048a56c559fff696989b8d067c19010cb0625031d5f7179aed73fb3af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolsToUseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33225dda814a25499e415dbea5c85f8fa9651f7d173627c6b95ae5229f95b1fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone": "availabilityZone",
        "instance_type": "instanceType",
    },
)
class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride:
    def __init__(
        self,
        *,
        availability_zone: builtins.str,
        instance_type: builtins.str,
    ) -> None:
        '''
        :param availability_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability_zone DataDatabricksInstancePool#availability_zone}.
        :param instance_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_type DataDatabricksInstancePool#instance_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf7daeb8b337206e94f3ee3c550d0ebd5bad89581a807c01ad7df89b7b9b14a)
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone": availability_zone,
            "instance_type": instance_type,
        }

    @builtins.property
    def availability_zone(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability_zone DataDatabricksInstancePool#availability_zone}.'''
        result = self._values.get("availability_zone")
        assert result is not None, "Required property 'availability_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_type DataDatabricksInstancePool#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca14e02c20490fcacb464e7278dd7b734ec0b6946b9c2c4ab10381032193ef7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2b69231c1c5654b8c4c87d7b193f264771d880799d3b9afae95ed11043663bd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfba10cae5547c4f6b5ccd3c808e9265dd7a676f0d21cf43530ef399472b4249)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a4fce519e079561fc2c86c9148382868276c0ea6651e4d04334144f6d419f1f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c45df22d8c00a4a87d2e5b1715781020cf64eadc28691a1d115a8c2891d16a50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39164b33fe8fb956b42b4990291f1c9c37a2c00754bde43dde87df3dcf27d5ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98de8a83de5658a8758aa85ad6311e5ad471cf0cddc88592a8fd4b388ae6beb9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f7b96a1c13eba84e8f4fdb133fd7ca94744b3eef07c22cb751f58d77a581674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a25b1af93aad031e95f9c56fc8b2a1674fc4b7e0e7c8226d80494050bff4bd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331e41542c63061414cd66d51e24f74f05a8651f9674931902d24bf1e5180558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c5b16f9a4b1f2081835e5bdeb5082f0861324ff8784138eb9267a2c05a29f84)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fefb4faefae3bc66eb7219c7223991dc2ba4b89e09bed96b9115ed2db6275fbe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8888f6658ab8dc1f385450c88ed7d0994f28c0db579bbb04c91944ee8cffc44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5184786715e9b0a77ddec8eca6ddcbd13cfaee2de0ccda633d7b808c573975cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b177fe55b69a405add322f51cef41e6af5d58181e562afa355efe4c2b67403c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cacfff45503d71ed0a984cb395b72098b3d1a0c46ed3ebc0d8c39f9889a694a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__adf59df298515a46acfd8066443d2badec9f6201d07f529dafc3c00571cee270)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFleetOnDemandOption")
    def put_fleet_on_demand_option(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.
        '''
        value = DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption(
            allocation_strategy=allocation_strategy,
            instance_pools_to_use_count=instance_pools_to_use_count,
        )

        return typing.cast(None, jsii.invoke(self, "putFleetOnDemandOption", [value]))

    @jsii.member(jsii_name="putFleetSpotOption")
    def put_fleet_spot_option(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#allocation_strategy DataDatabricksInstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#instance_pools_to_use_count DataDatabricksInstancePool#instance_pools_to_use_count}.
        '''
        value = DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption(
            allocation_strategy=allocation_strategy,
            instance_pools_to_use_count=instance_pools_to_use_count,
        )

        return typing.cast(None, jsii.invoke(self, "putFleetSpotOption", [value]))

    @jsii.member(jsii_name="putLaunchTemplateOverride")
    def put_launch_template_override(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5d96aa707c0d02f3264bb39867d3896a182c7a5cd5f0362f0ce81dddfc3708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLaunchTemplateOverride", [value]))

    @jsii.member(jsii_name="resetFleetOnDemandOption")
    def reset_fleet_on_demand_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFleetOnDemandOption", []))

    @jsii.member(jsii_name="resetFleetSpotOption")
    def reset_fleet_spot_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFleetSpotOption", []))

    @builtins.property
    @jsii.member(jsii_name="fleetOnDemandOption")
    def fleet_on_demand_option(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOptionOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOptionOutputReference, jsii.get(self, "fleetOnDemandOption"))

    @builtins.property
    @jsii.member(jsii_name="fleetSpotOption")
    def fleet_spot_option(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOptionOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOptionOutputReference, jsii.get(self, "fleetSpotOption"))

    @builtins.property
    @jsii.member(jsii_name="launchTemplateOverride")
    def launch_template_override(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideList:
        return typing.cast(DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideList, jsii.get(self, "launchTemplateOverride"))

    @builtins.property
    @jsii.member(jsii_name="fleetOnDemandOptionInput")
    def fleet_on_demand_option_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption], jsii.get(self, "fleetOnDemandOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="fleetSpotOptionInput")
    def fleet_spot_option_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption], jsii.get(self, "fleetSpotOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="launchTemplateOverrideInput")
    def launch_template_override_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]], jsii.get(self, "launchTemplateOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381781ef90ea3afe7fb68cf9de8ae9ce869ddc4fd1819fd0496708ee9949fa44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c554d790ffd5af0523f3029d9a53737a586350ed6459dfe637968fc9f0032fdb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAwsAttributes")
    def put_aws_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_price_percent DataDatabricksInstancePool#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.
        '''
        value = DataDatabricksInstancePoolPoolInfoAwsAttributes(
            availability=availability,
            spot_bid_price_percent=spot_bid_price_percent,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAwsAttributes", [value]))

    @jsii.member(jsii_name="putAzureAttributes")
    def put_azure_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#availability DataDatabricksInstancePool#availability}.
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#spot_bid_max_price DataDatabricksInstancePool#spot_bid_max_price}.
        '''
        value = DataDatabricksInstancePoolPoolInfoAzureAttributes(
            availability=availability, spot_bid_max_price=spot_bid_max_price
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAttributes", [value]))

    @jsii.member(jsii_name="putDiskSpec")
    def put_disk_spec(
        self,
        *,
        disk_count: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        disk_type: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param disk_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_count DataDatabricksInstancePool#disk_count}.
        :param disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_size DataDatabricksInstancePool#disk_size}.
        :param disk_type: disk_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#disk_type DataDatabricksInstancePool#disk_type}
        '''
        value = DataDatabricksInstancePoolPoolInfoDiskSpec(
            disk_count=disk_count, disk_size=disk_size, disk_type=disk_type
        )

        return typing.cast(None, jsii.invoke(self, "putDiskSpec", [value]))

    @jsii.member(jsii_name="putGcpAttributes")
    def put_gcp_attributes(
        self,
        *,
        gcp_availability: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param gcp_availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#gcp_availability DataDatabricksInstancePool#gcp_availability}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#local_ssd_count DataDatabricksInstancePool#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#zone_id DataDatabricksInstancePool#zone_id}.
        '''
        value = DataDatabricksInstancePoolPoolInfoGcpAttributes(
            gcp_availability=gcp_availability,
            local_ssd_count=local_ssd_count,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpAttributes", [value]))

    @jsii.member(jsii_name="putInstancePoolFleetAttributes")
    def put_instance_pool_fleet_attributes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__216ca147ceb31c9b3a80398eab749651c07153d658b6a04a1513741237f6d891)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInstancePoolFleetAttributes", [value]))

    @jsii.member(jsii_name="putPreloadedDockerImage")
    def put_preloaded_docker_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568780deaeb31a84134f83482c402f50c4f9d996bbc41c1f8074ad744feb80a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPreloadedDockerImage", [value]))

    @jsii.member(jsii_name="putStats")
    def put_stats(
        self,
        *,
        idle_count: typing.Optional[jsii.Number] = None,
        pending_idle_count: typing.Optional[jsii.Number] = None,
        pending_used_count: typing.Optional[jsii.Number] = None,
        used_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param idle_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_count DataDatabricksInstancePool#idle_count}.
        :param pending_idle_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_idle_count DataDatabricksInstancePool#pending_idle_count}.
        :param pending_used_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_used_count DataDatabricksInstancePool#pending_used_count}.
        :param used_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#used_count DataDatabricksInstancePool#used_count}.
        '''
        value = DataDatabricksInstancePoolPoolInfoStats(
            idle_count=idle_count,
            pending_idle_count=pending_idle_count,
            pending_used_count=pending_used_count,
            used_count=used_count,
        )

        return typing.cast(None, jsii.invoke(self, "putStats", [value]))

    @jsii.member(jsii_name="resetAwsAttributes")
    def reset_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAttributes", []))

    @jsii.member(jsii_name="resetAzureAttributes")
    def reset_azure_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAttributes", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDefaultTags")
    def reset_default_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTags", []))

    @jsii.member(jsii_name="resetDiskSpec")
    def reset_disk_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSpec", []))

    @jsii.member(jsii_name="resetEnableElasticDisk")
    def reset_enable_elastic_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableElasticDisk", []))

    @jsii.member(jsii_name="resetGcpAttributes")
    def reset_gcp_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAttributes", []))

    @jsii.member(jsii_name="resetInstancePoolFleetAttributes")
    def reset_instance_pool_fleet_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolFleetAttributes", []))

    @jsii.member(jsii_name="resetInstancePoolId")
    def reset_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolId", []))

    @jsii.member(jsii_name="resetMaxCapacity")
    def reset_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCapacity", []))

    @jsii.member(jsii_name="resetMinIdleInstances")
    def reset_min_idle_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinIdleInstances", []))

    @jsii.member(jsii_name="resetNodeTypeId")
    def reset_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeTypeId", []))

    @jsii.member(jsii_name="resetPreloadedDockerImage")
    def reset_preloaded_docker_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreloadedDockerImage", []))

    @jsii.member(jsii_name="resetPreloadedSparkVersions")
    def reset_preloaded_spark_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreloadedSparkVersions", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetStats")
    def reset_stats(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStats", []))

    @builtins.property
    @jsii.member(jsii_name="awsAttributes")
    def aws_attributes(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoAwsAttributesOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoAwsAttributesOutputReference, jsii.get(self, "awsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributes")
    def azure_attributes(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoAzureAttributesOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoAzureAttributesOutputReference, jsii.get(self, "azureAttributes"))

    @builtins.property
    @jsii.member(jsii_name="diskSpec")
    def disk_spec(self) -> DataDatabricksInstancePoolPoolInfoDiskSpecOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoDiskSpecOutputReference, jsii.get(self, "diskSpec"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributes")
    def gcp_attributes(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoGcpAttributesOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoGcpAttributesOutputReference, jsii.get(self, "gcpAttributes"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolFleetAttributes")
    def instance_pool_fleet_attributes(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesList:
        return typing.cast(DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesList, jsii.get(self, "instancePoolFleetAttributes"))

    @builtins.property
    @jsii.member(jsii_name="preloadedDockerImage")
    def preloaded_docker_image(
        self,
    ) -> "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageList":
        return typing.cast("DataDatabricksInstancePoolPoolInfoPreloadedDockerImageList", jsii.get(self, "preloadedDockerImage"))

    @builtins.property
    @jsii.member(jsii_name="stats")
    def stats(self) -> "DataDatabricksInstancePoolPoolInfoStatsOutputReference":
        return typing.cast("DataDatabricksInstancePoolPoolInfoStatsOutputReference", jsii.get(self, "stats"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributesInput")
    def aws_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes], jsii.get(self, "awsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributesInput")
    def azure_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes], jsii.get(self, "azureAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTagsInput")
    def default_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "defaultTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSpecInput")
    def disk_spec_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec], jsii.get(self, "diskSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="enableElasticDiskInput")
    def enable_elastic_disk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableElasticDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributesInput")
    def gcp_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes], jsii.get(self, "gcpAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="idleInstanceAutoterminationMinutesInput")
    def idle_instance_autotermination_minutes_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleInstanceAutoterminationMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolFleetAttributesInput")
    def instance_pool_fleet_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]], jsii.get(self, "instancePoolFleetAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolIdInput")
    def instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolNameInput")
    def instance_pool_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolNameInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCapacityInput")
    def max_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="minIdleInstancesInput")
    def min_idle_instances_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minIdleInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeIdInput")
    def node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="preloadedDockerImageInput")
    def preloaded_docker_image_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksInstancePoolPoolInfoPreloadedDockerImage"]]], jsii.get(self, "preloadedDockerImageInput"))

    @builtins.property
    @jsii.member(jsii_name="preloadedSparkVersionsInput")
    def preloaded_spark_versions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preloadedSparkVersionsInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="statsInput")
    def stats_input(self) -> typing.Optional["DataDatabricksInstancePoolPoolInfoStats"]:
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoStats"], jsii.get(self, "statsInput"))

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c48183f68391f74e7a5d22eca6512a0d319d40ae9c2bc4138c8d4ac6670f5fde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTags")
    def default_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "defaultTags"))

    @default_tags.setter
    def default_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7f44736395d4d5d79483181ffd3b137e6e5e2e17b180f09a5e148efba300ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableElasticDisk")
    def enable_elastic_disk(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableElasticDisk"))

    @enable_elastic_disk.setter
    def enable_elastic_disk(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7d0b6f9eba717855763cdc9f23b14d2555a4fd25702d47b9633e34b3f4b8ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableElasticDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idleInstanceAutoterminationMinutes")
    def idle_instance_autotermination_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleInstanceAutoterminationMinutes"))

    @idle_instance_autotermination_minutes.setter
    def idle_instance_autotermination_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a231f110ee6846b9d6e41b95406372a80a7c95b179a97ab457b49aec126c3952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleInstanceAutoterminationMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2521ee1f0e0476df86c136c29e75a432cd2ac67269d79e1c244c87259453e045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolName")
    def instance_pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolName"))

    @instance_pool_name.setter
    def instance_pool_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11668617c2422a30ced439380354ce7d45635db1f9f2cec956262cd0a57d0753)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__448c167e78d05fa0a89fc8733e67d3ca9b57cae6d086f759d56c7a649250e44d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minIdleInstances")
    def min_idle_instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minIdleInstances"))

    @min_idle_instances.setter
    def min_idle_instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3120ddc89d796c2916cab308ef7b237db06b83b712f8f1366a998f21f239aa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minIdleInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74c40e5ae7663dadb53a14e707e52c817c6b321ca59c4220db8a84534820021c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preloadedSparkVersions")
    def preloaded_spark_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preloadedSparkVersions"))

    @preloaded_spark_versions.setter
    def preloaded_spark_versions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef028b416c7067e90038e04f9ae309e8d5031a9ce872acf147d273a74edeaf0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preloadedSparkVersions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d75359be16097a82dd14685ed7a58fc9e4637370a9aff4d04c71cc0f672da4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksInstancePoolPoolInfo]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac8f3463ee688e93a204cc37c2af2705f8f910f33d9a61eeef2e1250b20f01cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoPreloadedDockerImage",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "basic_auth": "basicAuth"},
)
class DataDatabricksInstancePoolPoolInfoPreloadedDockerImage:
    def __init__(
        self,
        *,
        url: builtins.str,
        basic_auth: typing.Optional[typing.Union["DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#url DataDatabricksInstancePool#url}.
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#basic_auth DataDatabricksInstancePool#basic_auth}
        '''
        if isinstance(basic_auth, dict):
            basic_auth = DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24334c7bcd411e083a4d792b3173425457f80689e59820b9434d1e8df8417eac)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#url DataDatabricksInstancePool#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth(
        self,
    ) -> typing.Optional["DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth"]:
        '''basic_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#basic_auth DataDatabricksInstancePool#basic_auth}
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoPreloadedDockerImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#password DataDatabricksInstancePool#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#username DataDatabricksInstancePool#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__748d8f911c00b9d049d1e5cf0e1612ff3f7119ba5e6697ead434baf85a7dcd0f)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#password DataDatabricksInstancePool#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#username DataDatabricksInstancePool#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ed9f6d2d12868cc7007c83f466eb5fe01884059397d0c91d1100619d19db55c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7da982a7a4d76f38daafbca83cc16d070be71e9204a06829eed27364fa5e0f9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b1989b40989b6b8c4e5274f9934360728c4888b609cce498da4f3d0bac3e25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1438766c7a7be405bb4d74d3b8f426e81af1cd73862fc77d14985fd7cc2f6828)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoPreloadedDockerImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoPreloadedDockerImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6890060206a843619ff7471ed0ec22411a0ce6d0cfd48799b995f61155fd5d20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0445f70cff4a4fc84c8f15f8e703ef168da04309ac67c5320117174b63834946)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksInstancePoolPoolInfoPreloadedDockerImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d21013091b5be3e810ab700922ce3e733ce877f9dd41617d2cdd3baeab2943d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__43b95de9af6a246ec3a933113b49d18c16f888621d34f44fd2c5682c08b2b9d2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4e29b802081685f114a094b5b33936e390178c15e6777fa3987c34a40863fd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2535e69188173edddd427368d30aa66b78768445dab365f93cb340b0198a3ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksInstancePoolPoolInfoPreloadedDockerImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoPreloadedDockerImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c32563fc8978029fbfd2222e07ca419150537c440ab7d57970d666c40456c27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putBasicAuth")
    def put_basic_auth(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#password DataDatabricksInstancePool#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#username DataDatabricksInstancePool#username}.
        '''
        value = DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth(
            password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putBasicAuth", [value]))

    @jsii.member(jsii_name="resetBasicAuth")
    def reset_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuth", []))

    @builtins.property
    @jsii.member(jsii_name="basicAuth")
    def basic_auth(
        self,
    ) -> DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuthOutputReference:
        return typing.cast(DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuthOutputReference, jsii.get(self, "basicAuth"))

    @builtins.property
    @jsii.member(jsii_name="basicAuthInput")
    def basic_auth_input(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth], jsii.get(self, "basicAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba7aabfb155037e01746009121a762f7ddb52a1a7d9f8461ec219a82b8ee6fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a3b6bf002c3a3847c45a6fe4890fb1c7080840835063b4ef33768c972c290a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoStats",
    jsii_struct_bases=[],
    name_mapping={
        "idle_count": "idleCount",
        "pending_idle_count": "pendingIdleCount",
        "pending_used_count": "pendingUsedCount",
        "used_count": "usedCount",
    },
)
class DataDatabricksInstancePoolPoolInfoStats:
    def __init__(
        self,
        *,
        idle_count: typing.Optional[jsii.Number] = None,
        pending_idle_count: typing.Optional[jsii.Number] = None,
        pending_used_count: typing.Optional[jsii.Number] = None,
        used_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param idle_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_count DataDatabricksInstancePool#idle_count}.
        :param pending_idle_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_idle_count DataDatabricksInstancePool#pending_idle_count}.
        :param pending_used_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_used_count DataDatabricksInstancePool#pending_used_count}.
        :param used_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#used_count DataDatabricksInstancePool#used_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80df0d9e86b355cb378b8e361fac3717f54df811621596b9327a78a748188c8b)
            check_type(argname="argument idle_count", value=idle_count, expected_type=type_hints["idle_count"])
            check_type(argname="argument pending_idle_count", value=pending_idle_count, expected_type=type_hints["pending_idle_count"])
            check_type(argname="argument pending_used_count", value=pending_used_count, expected_type=type_hints["pending_used_count"])
            check_type(argname="argument used_count", value=used_count, expected_type=type_hints["used_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if idle_count is not None:
            self._values["idle_count"] = idle_count
        if pending_idle_count is not None:
            self._values["pending_idle_count"] = pending_idle_count
        if pending_used_count is not None:
            self._values["pending_used_count"] = pending_used_count
        if used_count is not None:
            self._values["used_count"] = used_count

    @builtins.property
    def idle_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#idle_count DataDatabricksInstancePool#idle_count}.'''
        result = self._values.get("idle_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pending_idle_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_idle_count DataDatabricksInstancePool#pending_idle_count}.'''
        result = self._values.get("pending_idle_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pending_used_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#pending_used_count DataDatabricksInstancePool#pending_used_count}.'''
        result = self._values.get("pending_used_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def used_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/instance_pool#used_count DataDatabricksInstancePool#used_count}.'''
        result = self._values.get("used_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksInstancePoolPoolInfoStats(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksInstancePoolPoolInfoStatsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksInstancePool.DataDatabricksInstancePoolPoolInfoStatsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3839e508f7f506f2c17ca1299d846f97e5207d20860db52fad561c97d77861e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIdleCount")
    def reset_idle_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleCount", []))

    @jsii.member(jsii_name="resetPendingIdleCount")
    def reset_pending_idle_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPendingIdleCount", []))

    @jsii.member(jsii_name="resetPendingUsedCount")
    def reset_pending_used_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPendingUsedCount", []))

    @jsii.member(jsii_name="resetUsedCount")
    def reset_used_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsedCount", []))

    @builtins.property
    @jsii.member(jsii_name="idleCountInput")
    def idle_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleCountInput"))

    @builtins.property
    @jsii.member(jsii_name="pendingIdleCountInput")
    def pending_idle_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pendingIdleCountInput"))

    @builtins.property
    @jsii.member(jsii_name="pendingUsedCountInput")
    def pending_used_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pendingUsedCountInput"))

    @builtins.property
    @jsii.member(jsii_name="usedCountInput")
    def used_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "usedCountInput"))

    @builtins.property
    @jsii.member(jsii_name="idleCount")
    def idle_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleCount"))

    @idle_count.setter
    def idle_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a98830e36c7c6d5077697e6fc602cb1e843722dfadbcc40b4e1b02b9458a3be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pendingIdleCount")
    def pending_idle_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pendingIdleCount"))

    @pending_idle_count.setter
    def pending_idle_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__490341b44057dce4d5e456f0eb6ddbe7a3fd2d93b7927681a5c20f6c1dd4555e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pendingIdleCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pendingUsedCount")
    def pending_used_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pendingUsedCount"))

    @pending_used_count.setter
    def pending_used_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5e161b8368e55cbca8648e409be9d8e6e7cfc385e02c32c41de953c576a51f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pendingUsedCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usedCount")
    def used_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "usedCount"))

    @used_count.setter
    def used_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4d803d9502bfe0781bdb461423bd23ac49b1dc1fa216c5791abf712cae9b7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usedCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksInstancePoolPoolInfoStats]:
        return typing.cast(typing.Optional[DataDatabricksInstancePoolPoolInfoStats], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksInstancePoolPoolInfoStats],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331d36c9fb615589ef1c6d0e993213c368597d780d1ffc2b617a17db0ed7719a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksInstancePool",
    "DataDatabricksInstancePoolConfig",
    "DataDatabricksInstancePoolPoolInfo",
    "DataDatabricksInstancePoolPoolInfoAwsAttributes",
    "DataDatabricksInstancePoolPoolInfoAwsAttributesOutputReference",
    "DataDatabricksInstancePoolPoolInfoAzureAttributes",
    "DataDatabricksInstancePoolPoolInfoAzureAttributesOutputReference",
    "DataDatabricksInstancePoolPoolInfoDiskSpec",
    "DataDatabricksInstancePoolPoolInfoDiskSpecDiskType",
    "DataDatabricksInstancePoolPoolInfoDiskSpecDiskTypeOutputReference",
    "DataDatabricksInstancePoolPoolInfoDiskSpecOutputReference",
    "DataDatabricksInstancePoolPoolInfoGcpAttributes",
    "DataDatabricksInstancePoolPoolInfoGcpAttributesOutputReference",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOptionOutputReference",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOptionOutputReference",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideList",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesList",
    "DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesOutputReference",
    "DataDatabricksInstancePoolPoolInfoOutputReference",
    "DataDatabricksInstancePoolPoolInfoPreloadedDockerImage",
    "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth",
    "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuthOutputReference",
    "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageList",
    "DataDatabricksInstancePoolPoolInfoPreloadedDockerImageOutputReference",
    "DataDatabricksInstancePoolPoolInfoStats",
    "DataDatabricksInstancePoolPoolInfoStatsOutputReference",
]

publication.publish()

def _typecheckingstub__06c9b25c5147765a557f1f0ad8681343ca321a784ea18d6a49dd362ef828c084(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    pool_info: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfo, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__f5099b803ecfad924f1464bb26bff495b842e304b5e19ed1daa85d36e86686e9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd0b9f094868163cd882a994ea3a5ad643453c6b0f2071a56b0a6160eb78e544(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__207197444fdbde2682499dc73f7eb9ea3cd24958c32fe4b458f5b04f5c17e147(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4886511e6d711662977562a730a725479a50b233e19b52f8e429acad645297ba(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    pool_info: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfo, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a04c76888462ad56259b8a7d77e6b5d968bf8036432aae0a5812523ba89ab858(
    *,
    idle_instance_autotermination_minutes: jsii.Number,
    instance_pool_name: builtins.str,
    aws_attributes: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disk_spec: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoDiskSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gcp_attributes: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_pool_fleet_attributes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    min_idle_instances: typing.Optional[jsii.Number] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    state: typing.Optional[builtins.str] = None,
    stats: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoStats, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc6dd9a31b27335c60098d5d62a5fc919b8ba52f3008ccc0dfb76a2d200804c9(
    *,
    availability: typing.Optional[builtins.str] = None,
    spot_bid_price_percent: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc23a07bd96c35abcf9f9aa10f45916745df9a27e82f08ab4f2c25bc080d799f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea68c10754aba3db42806a82d5a4037ab9e5a5252298077e2dd45fb23bc427c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01829f38cb2ac8e2e4ebdd0334f4179e8be7e2980e6ba423a559cc11664afd0b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b38e2cac5e9ce6e003ec79c4c1ab0231124a4e88feac5ab06842fb23b21e5dfd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13afe210d5408b9a52f5b7e9c90afbdf55bf126f71705cb88d18be7fb7146e4(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ce15ae9944a723a6ebe2117c618de2266f73f17376e5b2f21928b7c5573bd93(
    *,
    availability: typing.Optional[builtins.str] = None,
    spot_bid_max_price: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c5ff60be5ca782c2ce865b5b78658cea89cea156d89929688d0468929daf05f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2daf2588b0c622770e8179a7c6329b7e5205278eb6ceae39d747c30705bd40fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0781c6198387d55928dd37ccf1e761a279c88019d4a01e58f719dd742e0b9246(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae08292ffd33227158e946eab2c9bb47a289d6afbb2951b58d64c4c6ddc45e7(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoAzureAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c9ad16008a2caabcf33de7aa2f8e47ee23cbf0d995987800f2e8a8b161b754(
    *,
    disk_count: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    disk_type: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89478803c566b8c2597263e5eb6bc110fc0e9319a8dfc96817f410c0ececef70(
    *,
    azure_disk_volume_type: typing.Optional[builtins.str] = None,
    ebs_volume_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7d4aeb00b919fc8762e5dc6dbd072d7f3338ce1fa38c2d8fcd6027ffcd62d78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74aeffe39a0a211c1635d5d2aa4513cb841f2dd6b47ea265055f30eab73ea44f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8079e482ec956c6fe17a2203b90a02f64b671e0844c2f07f2a9c107bffaabbab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4202000dd5f4367d2c6d5827ee2d92472b8fe989e580bb726cb16f8d3b63b4aa(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpecDiskType],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5764fd1b4760e200952757288e859c0d6dce4df3bb3701af75472ac93aad00c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a1bc483560b5995d533b17f9dc9f8e65e9b7dbe7a652a17ae878731efaa6d2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc6573caa0f7027ac5da5cb8b51c68a340161035214fb9486512c35ed680456(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90c32a9751ff77860ab075d6619c8aab17e66639fbd49e977926046adf3f0a43(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoDiskSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac073e583f1e0f1984dc21b57638a368786cd5091f95f629f9d973e2bfaee437(
    *,
    gcp_availability: typing.Optional[builtins.str] = None,
    local_ssd_count: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__623ba4b8a406ea7fd0d14ac3a35acd71591031a67883db2b68ae5c0cdc0337d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e47eb9bdd5904a0aeadefe9de34e15b32ceec8c979023aed05064dfefcfacde3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dd63e60eb25fbd6b083680a955b284f9a3d89a76cec03cb49b32a8743cee804(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29125e44588c94ead02f9474c845bdc0e75491aca698842eee35af144ab0aa6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c1de4aa407300724cd47fa1c0d694eac8ae18b96592c42412eabfeaacd79d3(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoGcpAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__004f263e57574d172f155674ed274dd16b2f777275665638edf78fb76d2ff9ac(
    *,
    launch_template_override: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
    fleet_on_demand_option: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption, typing.Dict[builtins.str, typing.Any]]] = None,
    fleet_spot_option: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc5cd545b560327bd77242ca1347c939d42e53f51f380694fc35481ed825e8a(
    *,
    allocation_strategy: builtins.str,
    instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9be92fb47249dbebf2575e73671c962f3ac4d3acf91f6af48de94e03db5c0c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1d659ffb15cb2841a05b5ee1a104131e459aa01cf2edbc7ce9ece5332f4033(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0707798a3a22168c8d36e94464aee6d730a73b82e2cd9d592022492c51445445(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ff022c892c40ef1fc055fed1417dc87e28109b61636f535a9a89b5ac979e799(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetOnDemandOption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ef06fa2cbe82b736b782367c2f507f26c1970e10984a756506833b617545c01(
    *,
    allocation_strategy: builtins.str,
    instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d43876023a55304b3cb05bb6281de649457886cdb632e628569b1d24b036528(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a4b0bc7a715a18b0c07224451e7c9014f908311ba421bdc87a6cd740abcdaa0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f4d9fe048a56c559fff696989b8d067c19010cb0625031d5f7179aed73fb3af(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33225dda814a25499e415dbea5c85f8fa9651f7d173627c6b95ae5229f95b1fd(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesFleetSpotOption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf7daeb8b337206e94f3ee3c550d0ebd5bad89581a807c01ad7df89b7b9b14a(
    *,
    availability_zone: builtins.str,
    instance_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca14e02c20490fcacb464e7278dd7b734ec0b6946b9c2c4ab10381032193ef7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b69231c1c5654b8c4c87d7b193f264771d880799d3b9afae95ed11043663bd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfba10cae5547c4f6b5ccd3c808e9265dd7a676f0d21cf43530ef399472b4249(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4fce519e079561fc2c86c9148382868276c0ea6651e4d04334144f6d419f1f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45df22d8c00a4a87d2e5b1715781020cf64eadc28691a1d115a8c2891d16a50(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39164b33fe8fb956b42b4990291f1c9c37a2c00754bde43dde87df3dcf27d5ad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98de8a83de5658a8758aa85ad6311e5ad471cf0cddc88592a8fd4b388ae6beb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7b96a1c13eba84e8f4fdb133fd7ca94744b3eef07c22cb751f58d77a581674(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a25b1af93aad031e95f9c56fc8b2a1674fc4b7e0e7c8226d80494050bff4bd0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331e41542c63061414cd66d51e24f74f05a8651f9674931902d24bf1e5180558(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c5b16f9a4b1f2081835e5bdeb5082f0861324ff8784138eb9267a2c05a29f84(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fefb4faefae3bc66eb7219c7223991dc2ba4b89e09bed96b9115ed2db6275fbe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8888f6658ab8dc1f385450c88ed7d0994f28c0db579bbb04c91944ee8cffc44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5184786715e9b0a77ddec8eca6ddcbd13cfaee2de0ccda633d7b808c573975cd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b177fe55b69a405add322f51cef41e6af5d58181e562afa355efe4c2b67403c1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cacfff45503d71ed0a984cb395b72098b3d1a0c46ed3ebc0d8c39f9889a694a3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adf59df298515a46acfd8066443d2badec9f6201d07f529dafc3c00571cee270(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5d96aa707c0d02f3264bb39867d3896a182c7a5cd5f0362f0ce81dddfc3708(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381781ef90ea3afe7fb68cf9de8ae9ce869ddc4fd1819fd0496708ee9949fa44(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c554d790ffd5af0523f3029d9a53737a586350ed6459dfe637968fc9f0032fdb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__216ca147ceb31c9b3a80398eab749651c07153d658b6a04a1513741237f6d891(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoInstancePoolFleetAttributes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568780deaeb31a84134f83482c402f50c4f9d996bbc41c1f8074ad744feb80a4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c48183f68391f74e7a5d22eca6512a0d319d40ae9c2bc4138c8d4ac6670f5fde(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7f44736395d4d5d79483181ffd3b137e6e5e2e17b180f09a5e148efba300ad9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7d0b6f9eba717855763cdc9f23b14d2555a4fd25702d47b9633e34b3f4b8ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a231f110ee6846b9d6e41b95406372a80a7c95b179a97ab457b49aec126c3952(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2521ee1f0e0476df86c136c29e75a432cd2ac67269d79e1c244c87259453e045(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11668617c2422a30ced439380354ce7d45635db1f9f2cec956262cd0a57d0753(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__448c167e78d05fa0a89fc8733e67d3ca9b57cae6d086f759d56c7a649250e44d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3120ddc89d796c2916cab308ef7b237db06b83b712f8f1366a998f21f239aa9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74c40e5ae7663dadb53a14e707e52c817c6b321ca59c4220db8a84534820021c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef028b416c7067e90038e04f9ae309e8d5031a9ce872acf147d273a74edeaf0a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d75359be16097a82dd14685ed7a58fc9e4637370a9aff4d04c71cc0f672da4de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac8f3463ee688e93a204cc37c2af2705f8f910f33d9a61eeef2e1250b20f01cd(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24334c7bcd411e083a4d792b3173425457f80689e59820b9434d1e8df8417eac(
    *,
    url: builtins.str,
    basic_auth: typing.Optional[typing.Union[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__748d8f911c00b9d049d1e5cf0e1612ff3f7119ba5e6697ead434baf85a7dcd0f(
    *,
    password: builtins.str,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ed9f6d2d12868cc7007c83f466eb5fe01884059397d0c91d1100619d19db55c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7da982a7a4d76f38daafbca83cc16d070be71e9204a06829eed27364fa5e0f9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b1989b40989b6b8c4e5274f9934360728c4888b609cce498da4f3d0bac3e25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1438766c7a7be405bb4d74d3b8f426e81af1cd73862fc77d14985fd7cc2f6828(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoPreloadedDockerImageBasicAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6890060206a843619ff7471ed0ec22411a0ce6d0cfd48799b995f61155fd5d20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0445f70cff4a4fc84c8f15f8e703ef168da04309ac67c5320117174b63834946(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d21013091b5be3e810ab700922ce3e733ce877f9dd41617d2cdd3baeab2943d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43b95de9af6a246ec3a933113b49d18c16f888621d34f44fd2c5682c08b2b9d2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4e29b802081685f114a094b5b33936e390178c15e6777fa3987c34a40863fd2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2535e69188173edddd427368d30aa66b78768445dab365f93cb340b0198a3ddb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c32563fc8978029fbfd2222e07ca419150537c440ab7d57970d666c40456c27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba7aabfb155037e01746009121a762f7ddb52a1a7d9f8461ec219a82b8ee6fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a3b6bf002c3a3847c45a6fe4890fb1c7080840835063b4ef33768c972c290a3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksInstancePoolPoolInfoPreloadedDockerImage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80df0d9e86b355cb378b8e361fac3717f54df811621596b9327a78a748188c8b(
    *,
    idle_count: typing.Optional[jsii.Number] = None,
    pending_idle_count: typing.Optional[jsii.Number] = None,
    pending_used_count: typing.Optional[jsii.Number] = None,
    used_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3839e508f7f506f2c17ca1299d846f97e5207d20860db52fad561c97d77861e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a98830e36c7c6d5077697e6fc602cb1e843722dfadbcc40b4e1b02b9458a3be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__490341b44057dce4d5e456f0eb6ddbe7a3fd2d93b7927681a5c20f6c1dd4555e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5e161b8368e55cbca8648e409be9d8e6e7cfc385e02c32c41de953c576a51f9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e4d803d9502bfe0781bdb461423bd23ac49b1dc1fa216c5791abf712cae9b7c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331d36c9fb615589ef1c6d0e993213c368597d780d1ffc2b617a17db0ed7719a(
    value: typing.Optional[DataDatabricksInstancePoolPoolInfoStats],
) -> None:
    """Type checking stubs"""
    pass
