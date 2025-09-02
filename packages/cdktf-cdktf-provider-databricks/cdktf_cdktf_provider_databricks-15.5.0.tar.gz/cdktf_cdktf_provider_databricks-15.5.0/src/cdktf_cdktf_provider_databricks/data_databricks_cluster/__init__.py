r'''
# `data_databricks_cluster`

Refer to the Terraform Registry for docs: [`data_databricks_cluster`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster).
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


class DataDatabricksCluster(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksCluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster databricks_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_info: typing.Optional[typing.Union["DataDatabricksClusterClusterInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster databricks_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.
        :param cluster_info: cluster_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_info DataDatabricksCluster#cluster_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#id DataDatabricksCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d133c2fd37787cfe43f23e1d478942cd52dc142a57aceadf6477ff7c50381355)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksClusterConfig(
            cluster_id=cluster_id,
            cluster_info=cluster_info,
            cluster_name=cluster_name,
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
        '''Generates CDKTF code for importing a DataDatabricksCluster resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksCluster to import.
        :param import_from_id: The id of the existing DataDatabricksCluster that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksCluster to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0016c77e21b1df6e1dbd79f7fade0623d63c05e92b4695ffd32856bf16c96478)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putClusterInfo")
    def put_cluster_info(
        self,
        *,
        autoscale: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAutoscale", typing.Dict[builtins.str, typing.Any]]] = None,
        autotermination_minutes: typing.Optional[jsii.Number] = None,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_cores: typing.Optional[jsii.Number] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_log_conf: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogConf", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_log_status: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_memory_mb: typing.Optional[jsii.Number] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        cluster_source: typing.Optional[builtins.str] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data_security_mode: typing.Optional[builtins.str] = None,
        default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_image: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDockerImage", typing.Dict[builtins.str, typing.Any]]] = None,
        driver: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDriver", typing.Dict[builtins.str, typing.Any]]] = None,
        driver_instance_pool_id: typing.Optional[builtins.str] = None,
        driver_node_type_id: typing.Optional[builtins.str] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        executors: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoExecutors", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoInitScripts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jdbc_port: typing.Optional[jsii.Number] = None,
        kind: typing.Optional[builtins.str] = None,
        last_restarted_time: typing.Optional[jsii.Number] = None,
        last_state_loss_time: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        num_workers: typing.Optional[jsii.Number] = None,
        policy_id: typing.Optional[builtins.str] = None,
        remote_disk_throughput: typing.Optional[jsii.Number] = None,
        runtime_engine: typing.Optional[builtins.str] = None,
        single_user_name: typing.Optional[builtins.str] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_context_id: typing.Optional[jsii.Number] = None,
        spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_version: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        start_time: typing.Optional[jsii.Number] = None,
        state: typing.Optional[builtins.str] = None,
        state_message: typing.Optional[builtins.str] = None,
        terminated_time: typing.Optional[jsii.Number] = None,
        termination_reason: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoTerminationReason", typing.Dict[builtins.str, typing.Any]]] = None,
        total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
        use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_type: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoWorkloadType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscale: autoscale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        :param autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autotermination_minutes DataDatabricksCluster#autotermination_minutes}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        :param cluster_cores: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_cores DataDatabricksCluster#cluster_cores}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.
        :param cluster_log_conf: cluster_log_conf block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        :param cluster_log_status: cluster_log_status block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_status DataDatabricksCluster#cluster_log_status}
        :param cluster_memory_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_memory_mb DataDatabricksCluster#cluster_memory_mb}.
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param cluster_source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_source DataDatabricksCluster#cluster_source}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#creator_user_name DataDatabricksCluster#creator_user_name}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.
        :param data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.
        :param default_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#default_tags DataDatabricksCluster#default_tags}.
        :param docker_image: docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        :param driver: driver block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver DataDatabricksCluster#driver}
        :param driver_instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.
        :param driver_node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.
        :param enable_local_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.
        :param executors: executors block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#executors DataDatabricksCluster#executors}
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        :param init_scripts: init_scripts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.
        :param is_single_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.
        :param jdbc_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jdbc_port DataDatabricksCluster#jdbc_port}.
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.
        :param last_restarted_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_restarted_time DataDatabricksCluster#last_restarted_time}.
        :param last_state_loss_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_state_loss_time DataDatabricksCluster#last_state_loss_time}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.
        :param num_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.
        :param remote_disk_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.
        :param runtime_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.
        :param single_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.
        :param spark_conf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.
        :param spark_context_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_context_id DataDatabricksCluster#spark_context_id}.
        :param spark_env_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.
        :param spark_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spec DataDatabricksCluster#spec}
        :param ssh_public_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.
        :param start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_time DataDatabricksCluster#start_time}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state DataDatabricksCluster#state}.
        :param state_message: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state_message DataDatabricksCluster#state_message}.
        :param terminated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#terminated_time DataDatabricksCluster#terminated_time}.
        :param termination_reason: termination_reason block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#termination_reason DataDatabricksCluster#termination_reason}
        :param total_initial_remote_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.
        :param use_ml_runtime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.
        :param workload_type: workload_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        value = DataDatabricksClusterClusterInfo(
            autoscale=autoscale,
            autotermination_minutes=autotermination_minutes,
            aws_attributes=aws_attributes,
            azure_attributes=azure_attributes,
            cluster_cores=cluster_cores,
            cluster_id=cluster_id,
            cluster_log_conf=cluster_log_conf,
            cluster_log_status=cluster_log_status,
            cluster_memory_mb=cluster_memory_mb,
            cluster_name=cluster_name,
            cluster_source=cluster_source,
            creator_user_name=creator_user_name,
            custom_tags=custom_tags,
            data_security_mode=data_security_mode,
            default_tags=default_tags,
            docker_image=docker_image,
            driver=driver,
            driver_instance_pool_id=driver_instance_pool_id,
            driver_node_type_id=driver_node_type_id,
            enable_elastic_disk=enable_elastic_disk,
            enable_local_disk_encryption=enable_local_disk_encryption,
            executors=executors,
            gcp_attributes=gcp_attributes,
            init_scripts=init_scripts,
            instance_pool_id=instance_pool_id,
            is_single_node=is_single_node,
            jdbc_port=jdbc_port,
            kind=kind,
            last_restarted_time=last_restarted_time,
            last_state_loss_time=last_state_loss_time,
            node_type_id=node_type_id,
            num_workers=num_workers,
            policy_id=policy_id,
            remote_disk_throughput=remote_disk_throughput,
            runtime_engine=runtime_engine,
            single_user_name=single_user_name,
            spark_conf=spark_conf,
            spark_context_id=spark_context_id,
            spark_env_vars=spark_env_vars,
            spark_version=spark_version,
            spec=spec,
            ssh_public_keys=ssh_public_keys,
            start_time=start_time,
            state=state,
            state_message=state_message,
            terminated_time=terminated_time,
            termination_reason=termination_reason,
            total_initial_remote_disk_size=total_initial_remote_disk_size,
            use_ml_runtime=use_ml_runtime,
            workload_type=workload_type,
        )

        return typing.cast(None, jsii.invoke(self, "putClusterInfo", [value]))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetClusterInfo")
    def reset_cluster_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterInfo", []))

    @jsii.member(jsii_name="resetClusterName")
    def reset_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterName", []))

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
    @jsii.member(jsii_name="clusterInfo")
    def cluster_info(self) -> "DataDatabricksClusterClusterInfoOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoOutputReference", jsii.get(self, "clusterInfo"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterInfoInput")
    def cluster_info_input(self) -> typing.Optional["DataDatabricksClusterClusterInfo"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfo"], jsii.get(self, "clusterInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1699c6d848ec00fbed18a9f53dd4386a43a0c9d2af33c5e47b8803879c8ee32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14b1f6c30036d34c5f75edd72d49dc0dec54c8f6254430e489472f8976ad78c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b1e08b76b622e3dd6d91d7dcdba3e2e0e80c418de24692c7e9c4c8027c38699)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfo",
    jsii_struct_bases=[],
    name_mapping={
        "autoscale": "autoscale",
        "autotermination_minutes": "autoterminationMinutes",
        "aws_attributes": "awsAttributes",
        "azure_attributes": "azureAttributes",
        "cluster_cores": "clusterCores",
        "cluster_id": "clusterId",
        "cluster_log_conf": "clusterLogConf",
        "cluster_log_status": "clusterLogStatus",
        "cluster_memory_mb": "clusterMemoryMb",
        "cluster_name": "clusterName",
        "cluster_source": "clusterSource",
        "creator_user_name": "creatorUserName",
        "custom_tags": "customTags",
        "data_security_mode": "dataSecurityMode",
        "default_tags": "defaultTags",
        "docker_image": "dockerImage",
        "driver": "driver",
        "driver_instance_pool_id": "driverInstancePoolId",
        "driver_node_type_id": "driverNodeTypeId",
        "enable_elastic_disk": "enableElasticDisk",
        "enable_local_disk_encryption": "enableLocalDiskEncryption",
        "executors": "executors",
        "gcp_attributes": "gcpAttributes",
        "init_scripts": "initScripts",
        "instance_pool_id": "instancePoolId",
        "is_single_node": "isSingleNode",
        "jdbc_port": "jdbcPort",
        "kind": "kind",
        "last_restarted_time": "lastRestartedTime",
        "last_state_loss_time": "lastStateLossTime",
        "node_type_id": "nodeTypeId",
        "num_workers": "numWorkers",
        "policy_id": "policyId",
        "remote_disk_throughput": "remoteDiskThroughput",
        "runtime_engine": "runtimeEngine",
        "single_user_name": "singleUserName",
        "spark_conf": "sparkConf",
        "spark_context_id": "sparkContextId",
        "spark_env_vars": "sparkEnvVars",
        "spark_version": "sparkVersion",
        "spec": "spec",
        "ssh_public_keys": "sshPublicKeys",
        "start_time": "startTime",
        "state": "state",
        "state_message": "stateMessage",
        "terminated_time": "terminatedTime",
        "termination_reason": "terminationReason",
        "total_initial_remote_disk_size": "totalInitialRemoteDiskSize",
        "use_ml_runtime": "useMlRuntime",
        "workload_type": "workloadType",
    },
)
class DataDatabricksClusterClusterInfo:
    def __init__(
        self,
        *,
        autoscale: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAutoscale", typing.Dict[builtins.str, typing.Any]]] = None,
        autotermination_minutes: typing.Optional[jsii.Number] = None,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_cores: typing.Optional[jsii.Number] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_log_conf: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogConf", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_log_status: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogStatus", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_memory_mb: typing.Optional[jsii.Number] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        cluster_source: typing.Optional[builtins.str] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data_security_mode: typing.Optional[builtins.str] = None,
        default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_image: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDockerImage", typing.Dict[builtins.str, typing.Any]]] = None,
        driver: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDriver", typing.Dict[builtins.str, typing.Any]]] = None,
        driver_instance_pool_id: typing.Optional[builtins.str] = None,
        driver_node_type_id: typing.Optional[builtins.str] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        executors: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoExecutors", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoInitScripts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jdbc_port: typing.Optional[jsii.Number] = None,
        kind: typing.Optional[builtins.str] = None,
        last_restarted_time: typing.Optional[jsii.Number] = None,
        last_state_loss_time: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        num_workers: typing.Optional[jsii.Number] = None,
        policy_id: typing.Optional[builtins.str] = None,
        remote_disk_throughput: typing.Optional[jsii.Number] = None,
        runtime_engine: typing.Optional[builtins.str] = None,
        single_user_name: typing.Optional[builtins.str] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_context_id: typing.Optional[jsii.Number] = None,
        spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_version: typing.Optional[builtins.str] = None,
        spec: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        start_time: typing.Optional[jsii.Number] = None,
        state: typing.Optional[builtins.str] = None,
        state_message: typing.Optional[builtins.str] = None,
        terminated_time: typing.Optional[jsii.Number] = None,
        termination_reason: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoTerminationReason", typing.Dict[builtins.str, typing.Any]]] = None,
        total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
        use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_type: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoWorkloadType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscale: autoscale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        :param autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autotermination_minutes DataDatabricksCluster#autotermination_minutes}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        :param cluster_cores: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_cores DataDatabricksCluster#cluster_cores}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.
        :param cluster_log_conf: cluster_log_conf block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        :param cluster_log_status: cluster_log_status block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_status DataDatabricksCluster#cluster_log_status}
        :param cluster_memory_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_memory_mb DataDatabricksCluster#cluster_memory_mb}.
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param cluster_source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_source DataDatabricksCluster#cluster_source}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#creator_user_name DataDatabricksCluster#creator_user_name}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.
        :param data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.
        :param default_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#default_tags DataDatabricksCluster#default_tags}.
        :param docker_image: docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        :param driver: driver block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver DataDatabricksCluster#driver}
        :param driver_instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.
        :param driver_node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.
        :param enable_local_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.
        :param executors: executors block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#executors DataDatabricksCluster#executors}
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        :param init_scripts: init_scripts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.
        :param is_single_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.
        :param jdbc_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jdbc_port DataDatabricksCluster#jdbc_port}.
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.
        :param last_restarted_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_restarted_time DataDatabricksCluster#last_restarted_time}.
        :param last_state_loss_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_state_loss_time DataDatabricksCluster#last_state_loss_time}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.
        :param num_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.
        :param remote_disk_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.
        :param runtime_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.
        :param single_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.
        :param spark_conf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.
        :param spark_context_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_context_id DataDatabricksCluster#spark_context_id}.
        :param spark_env_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.
        :param spark_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spec DataDatabricksCluster#spec}
        :param ssh_public_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.
        :param start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_time DataDatabricksCluster#start_time}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state DataDatabricksCluster#state}.
        :param state_message: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state_message DataDatabricksCluster#state_message}.
        :param terminated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#terminated_time DataDatabricksCluster#terminated_time}.
        :param termination_reason: termination_reason block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#termination_reason DataDatabricksCluster#termination_reason}
        :param total_initial_remote_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.
        :param use_ml_runtime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.
        :param workload_type: workload_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        if isinstance(autoscale, dict):
            autoscale = DataDatabricksClusterClusterInfoAutoscale(**autoscale)
        if isinstance(aws_attributes, dict):
            aws_attributes = DataDatabricksClusterClusterInfoAwsAttributes(**aws_attributes)
        if isinstance(azure_attributes, dict):
            azure_attributes = DataDatabricksClusterClusterInfoAzureAttributes(**azure_attributes)
        if isinstance(cluster_log_conf, dict):
            cluster_log_conf = DataDatabricksClusterClusterInfoClusterLogConf(**cluster_log_conf)
        if isinstance(cluster_log_status, dict):
            cluster_log_status = DataDatabricksClusterClusterInfoClusterLogStatus(**cluster_log_status)
        if isinstance(docker_image, dict):
            docker_image = DataDatabricksClusterClusterInfoDockerImage(**docker_image)
        if isinstance(driver, dict):
            driver = DataDatabricksClusterClusterInfoDriver(**driver)
        if isinstance(gcp_attributes, dict):
            gcp_attributes = DataDatabricksClusterClusterInfoGcpAttributes(**gcp_attributes)
        if isinstance(spec, dict):
            spec = DataDatabricksClusterClusterInfoSpec(**spec)
        if isinstance(termination_reason, dict):
            termination_reason = DataDatabricksClusterClusterInfoTerminationReason(**termination_reason)
        if isinstance(workload_type, dict):
            workload_type = DataDatabricksClusterClusterInfoWorkloadType(**workload_type)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aff56b34c6a8acca8a91fda42e2e8676c9973443a5d6dd43eb7430c934f05b0b)
            check_type(argname="argument autoscale", value=autoscale, expected_type=type_hints["autoscale"])
            check_type(argname="argument autotermination_minutes", value=autotermination_minutes, expected_type=type_hints["autotermination_minutes"])
            check_type(argname="argument aws_attributes", value=aws_attributes, expected_type=type_hints["aws_attributes"])
            check_type(argname="argument azure_attributes", value=azure_attributes, expected_type=type_hints["azure_attributes"])
            check_type(argname="argument cluster_cores", value=cluster_cores, expected_type=type_hints["cluster_cores"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument cluster_log_conf", value=cluster_log_conf, expected_type=type_hints["cluster_log_conf"])
            check_type(argname="argument cluster_log_status", value=cluster_log_status, expected_type=type_hints["cluster_log_status"])
            check_type(argname="argument cluster_memory_mb", value=cluster_memory_mb, expected_type=type_hints["cluster_memory_mb"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument cluster_source", value=cluster_source, expected_type=type_hints["cluster_source"])
            check_type(argname="argument creator_user_name", value=creator_user_name, expected_type=type_hints["creator_user_name"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument data_security_mode", value=data_security_mode, expected_type=type_hints["data_security_mode"])
            check_type(argname="argument default_tags", value=default_tags, expected_type=type_hints["default_tags"])
            check_type(argname="argument docker_image", value=docker_image, expected_type=type_hints["docker_image"])
            check_type(argname="argument driver", value=driver, expected_type=type_hints["driver"])
            check_type(argname="argument driver_instance_pool_id", value=driver_instance_pool_id, expected_type=type_hints["driver_instance_pool_id"])
            check_type(argname="argument driver_node_type_id", value=driver_node_type_id, expected_type=type_hints["driver_node_type_id"])
            check_type(argname="argument enable_elastic_disk", value=enable_elastic_disk, expected_type=type_hints["enable_elastic_disk"])
            check_type(argname="argument enable_local_disk_encryption", value=enable_local_disk_encryption, expected_type=type_hints["enable_local_disk_encryption"])
            check_type(argname="argument executors", value=executors, expected_type=type_hints["executors"])
            check_type(argname="argument gcp_attributes", value=gcp_attributes, expected_type=type_hints["gcp_attributes"])
            check_type(argname="argument init_scripts", value=init_scripts, expected_type=type_hints["init_scripts"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument is_single_node", value=is_single_node, expected_type=type_hints["is_single_node"])
            check_type(argname="argument jdbc_port", value=jdbc_port, expected_type=type_hints["jdbc_port"])
            check_type(argname="argument kind", value=kind, expected_type=type_hints["kind"])
            check_type(argname="argument last_restarted_time", value=last_restarted_time, expected_type=type_hints["last_restarted_time"])
            check_type(argname="argument last_state_loss_time", value=last_state_loss_time, expected_type=type_hints["last_state_loss_time"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument num_workers", value=num_workers, expected_type=type_hints["num_workers"])
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
            check_type(argname="argument remote_disk_throughput", value=remote_disk_throughput, expected_type=type_hints["remote_disk_throughput"])
            check_type(argname="argument runtime_engine", value=runtime_engine, expected_type=type_hints["runtime_engine"])
            check_type(argname="argument single_user_name", value=single_user_name, expected_type=type_hints["single_user_name"])
            check_type(argname="argument spark_conf", value=spark_conf, expected_type=type_hints["spark_conf"])
            check_type(argname="argument spark_context_id", value=spark_context_id, expected_type=type_hints["spark_context_id"])
            check_type(argname="argument spark_env_vars", value=spark_env_vars, expected_type=type_hints["spark_env_vars"])
            check_type(argname="argument spark_version", value=spark_version, expected_type=type_hints["spark_version"])
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
            check_type(argname="argument ssh_public_keys", value=ssh_public_keys, expected_type=type_hints["ssh_public_keys"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument state_message", value=state_message, expected_type=type_hints["state_message"])
            check_type(argname="argument terminated_time", value=terminated_time, expected_type=type_hints["terminated_time"])
            check_type(argname="argument termination_reason", value=termination_reason, expected_type=type_hints["termination_reason"])
            check_type(argname="argument total_initial_remote_disk_size", value=total_initial_remote_disk_size, expected_type=type_hints["total_initial_remote_disk_size"])
            check_type(argname="argument use_ml_runtime", value=use_ml_runtime, expected_type=type_hints["use_ml_runtime"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autoscale is not None:
            self._values["autoscale"] = autoscale
        if autotermination_minutes is not None:
            self._values["autotermination_minutes"] = autotermination_minutes
        if aws_attributes is not None:
            self._values["aws_attributes"] = aws_attributes
        if azure_attributes is not None:
            self._values["azure_attributes"] = azure_attributes
        if cluster_cores is not None:
            self._values["cluster_cores"] = cluster_cores
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if cluster_log_conf is not None:
            self._values["cluster_log_conf"] = cluster_log_conf
        if cluster_log_status is not None:
            self._values["cluster_log_status"] = cluster_log_status
        if cluster_memory_mb is not None:
            self._values["cluster_memory_mb"] = cluster_memory_mb
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if cluster_source is not None:
            self._values["cluster_source"] = cluster_source
        if creator_user_name is not None:
            self._values["creator_user_name"] = creator_user_name
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if data_security_mode is not None:
            self._values["data_security_mode"] = data_security_mode
        if default_tags is not None:
            self._values["default_tags"] = default_tags
        if docker_image is not None:
            self._values["docker_image"] = docker_image
        if driver is not None:
            self._values["driver"] = driver
        if driver_instance_pool_id is not None:
            self._values["driver_instance_pool_id"] = driver_instance_pool_id
        if driver_node_type_id is not None:
            self._values["driver_node_type_id"] = driver_node_type_id
        if enable_elastic_disk is not None:
            self._values["enable_elastic_disk"] = enable_elastic_disk
        if enable_local_disk_encryption is not None:
            self._values["enable_local_disk_encryption"] = enable_local_disk_encryption
        if executors is not None:
            self._values["executors"] = executors
        if gcp_attributes is not None:
            self._values["gcp_attributes"] = gcp_attributes
        if init_scripts is not None:
            self._values["init_scripts"] = init_scripts
        if instance_pool_id is not None:
            self._values["instance_pool_id"] = instance_pool_id
        if is_single_node is not None:
            self._values["is_single_node"] = is_single_node
        if jdbc_port is not None:
            self._values["jdbc_port"] = jdbc_port
        if kind is not None:
            self._values["kind"] = kind
        if last_restarted_time is not None:
            self._values["last_restarted_time"] = last_restarted_time
        if last_state_loss_time is not None:
            self._values["last_state_loss_time"] = last_state_loss_time
        if node_type_id is not None:
            self._values["node_type_id"] = node_type_id
        if num_workers is not None:
            self._values["num_workers"] = num_workers
        if policy_id is not None:
            self._values["policy_id"] = policy_id
        if remote_disk_throughput is not None:
            self._values["remote_disk_throughput"] = remote_disk_throughput
        if runtime_engine is not None:
            self._values["runtime_engine"] = runtime_engine
        if single_user_name is not None:
            self._values["single_user_name"] = single_user_name
        if spark_conf is not None:
            self._values["spark_conf"] = spark_conf
        if spark_context_id is not None:
            self._values["spark_context_id"] = spark_context_id
        if spark_env_vars is not None:
            self._values["spark_env_vars"] = spark_env_vars
        if spark_version is not None:
            self._values["spark_version"] = spark_version
        if spec is not None:
            self._values["spec"] = spec
        if ssh_public_keys is not None:
            self._values["ssh_public_keys"] = ssh_public_keys
        if start_time is not None:
            self._values["start_time"] = start_time
        if state is not None:
            self._values["state"] = state
        if state_message is not None:
            self._values["state_message"] = state_message
        if terminated_time is not None:
            self._values["terminated_time"] = terminated_time
        if termination_reason is not None:
            self._values["termination_reason"] = termination_reason
        if total_initial_remote_disk_size is not None:
            self._values["total_initial_remote_disk_size"] = total_initial_remote_disk_size
        if use_ml_runtime is not None:
            self._values["use_ml_runtime"] = use_ml_runtime
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def autoscale(self) -> typing.Optional["DataDatabricksClusterClusterInfoAutoscale"]:
        '''autoscale block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        '''
        result = self._values.get("autoscale")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoAutoscale"], result)

    @builtins.property
    def autotermination_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autotermination_minutes DataDatabricksCluster#autotermination_minutes}.'''
        result = self._values.get("autotermination_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def aws_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoAwsAttributes"]:
        '''aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        '''
        result = self._values.get("aws_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoAwsAttributes"], result)

    @builtins.property
    def azure_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoAzureAttributes"]:
        '''azure_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        '''
        result = self._values.get("azure_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoAzureAttributes"], result)

    @builtins.property
    def cluster_cores(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_cores DataDatabricksCluster#cluster_cores}.'''
        result = self._values.get("cluster_cores")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_log_conf(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConf"]:
        '''cluster_log_conf block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        '''
        result = self._values.get("cluster_log_conf")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConf"], result)

    @builtins.property
    def cluster_log_status(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogStatus"]:
        '''cluster_log_status block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_status DataDatabricksCluster#cluster_log_status}
        '''
        result = self._values.get("cluster_log_status")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogStatus"], result)

    @builtins.property
    def cluster_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_memory_mb DataDatabricksCluster#cluster_memory_mb}.'''
        result = self._values.get("cluster_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_source DataDatabricksCluster#cluster_source}.'''
        result = self._values.get("cluster_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creator_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#creator_user_name DataDatabricksCluster#creator_user_name}.'''
        result = self._values.get("creator_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def data_security_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.'''
        result = self._values.get("data_security_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#default_tags DataDatabricksCluster#default_tags}.'''
        result = self._values.get("default_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def docker_image(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoDockerImage"]:
        '''docker_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        '''
        result = self._values.get("docker_image")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoDockerImage"], result)

    @builtins.property
    def driver(self) -> typing.Optional["DataDatabricksClusterClusterInfoDriver"]:
        '''driver block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver DataDatabricksCluster#driver}
        '''
        result = self._values.get("driver")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoDriver"], result)

    @builtins.property
    def driver_instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.'''
        result = self._values.get("driver_instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.'''
        result = self._values.get("driver_node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_elastic_disk(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.'''
        result = self._values.get("enable_elastic_disk")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_local_disk_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.'''
        result = self._values.get("enable_local_disk_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def executors(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoExecutors"]]]:
        '''executors block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#executors DataDatabricksCluster#executors}
        '''
        result = self._values.get("executors")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoExecutors"]]], result)

    @builtins.property
    def gcp_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoGcpAttributes"]:
        '''gcp_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        '''
        result = self._values.get("gcp_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoGcpAttributes"], result)

    @builtins.property
    def init_scripts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoInitScripts"]]]:
        '''init_scripts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        '''
        result = self._values.get("init_scripts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoInitScripts"]]], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_single_node(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.'''
        result = self._values.get("is_single_node")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def jdbc_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jdbc_port DataDatabricksCluster#jdbc_port}.'''
        result = self._values.get("jdbc_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kind(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.'''
        result = self._values.get("kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_restarted_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_restarted_time DataDatabricksCluster#last_restarted_time}.'''
        result = self._values.get("last_restarted_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def last_state_loss_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_state_loss_time DataDatabricksCluster#last_state_loss_time}.'''
        result = self._values.get("last_state_loss_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.'''
        result = self._values.get("node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.'''
        result = self._values.get("num_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.'''
        result = self._values.get("policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_disk_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.'''
        result = self._values.get("remote_disk_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def runtime_engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.'''
        result = self._values.get("runtime_engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def single_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.'''
        result = self._values.get("single_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_conf(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.'''
        result = self._values.get("spark_conf")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def spark_context_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_context_id DataDatabricksCluster#spark_context_id}.'''
        result = self._values.get("spark_context_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spark_env_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.'''
        result = self._values.get("spark_env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def spark_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.'''
        result = self._values.get("spark_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spec(self) -> typing.Optional["DataDatabricksClusterClusterInfoSpec"]:
        '''spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spec DataDatabricksCluster#spec}
        '''
        result = self._values.get("spec")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpec"], result)

    @builtins.property
    def ssh_public_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.'''
        result = self._values.get("ssh_public_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def start_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_time DataDatabricksCluster#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state DataDatabricksCluster#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#state_message DataDatabricksCluster#state_message}.'''
        result = self._values.get("state_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def terminated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#terminated_time DataDatabricksCluster#terminated_time}.'''
        result = self._values.get("terminated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def termination_reason(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoTerminationReason"]:
        '''termination_reason block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#termination_reason DataDatabricksCluster#termination_reason}
        '''
        result = self._values.get("termination_reason")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoTerminationReason"], result)

    @builtins.property
    def total_initial_remote_disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.'''
        result = self._values.get("total_initial_remote_disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def use_ml_runtime(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.'''
        result = self._values.get("use_ml_runtime")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_type(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoWorkloadType"]:
        '''workload_type block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoWorkloadType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAutoscale",
    jsii_struct_bases=[],
    name_mapping={"max_workers": "maxWorkers", "min_workers": "minWorkers"},
)
class DataDatabricksClusterClusterInfoAutoscale:
    def __init__(
        self,
        *,
        max_workers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e611460c20d10cf5c9c52b420e6d78c49d6eae8b4d26c09982229c9983ffb68d)
            check_type(argname="argument max_workers", value=max_workers, expected_type=type_hints["max_workers"])
            check_type(argname="argument min_workers", value=min_workers, expected_type=type_hints["min_workers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_workers is not None:
            self._values["max_workers"] = max_workers
        if min_workers is not None:
            self._values["min_workers"] = min_workers

    @builtins.property
    def max_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.'''
        result = self._values.get("max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.'''
        result = self._values.get("min_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoAutoscale(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoAutoscaleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAutoscaleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35752c886237667ffca38ea033402a4e9333b885632e81a2fdba0ea08174af11)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxWorkers")
    def reset_max_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWorkers", []))

    @jsii.member(jsii_name="resetMinWorkers")
    def reset_min_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinWorkers", []))

    @builtins.property
    @jsii.member(jsii_name="maxWorkersInput")
    def max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="minWorkersInput")
    def min_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkers")
    def max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkers"))

    @max_workers.setter
    def max_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14dc64da28b5cfd0c61243c07e441d9d2af1cd1d1b83ad793d43f1e16e1a705a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minWorkers")
    def min_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minWorkers"))

    @min_workers.setter
    def min_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c1fa899208a7be3f7baf39c8f39d706c6d8e94b1397c6a09e4a8fe3f8c74f3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAutoscale]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAutoscale], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoAutoscale],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__337c2d0342fca3dddf815ca98a3797af7bc5fad84fff22adb1d9d9db6e116476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "ebs_volume_count": "ebsVolumeCount",
        "ebs_volume_iops": "ebsVolumeIops",
        "ebs_volume_size": "ebsVolumeSize",
        "ebs_volume_throughput": "ebsVolumeThroughput",
        "ebs_volume_type": "ebsVolumeType",
        "first_on_demand": "firstOnDemand",
        "instance_profile_arn": "instanceProfileArn",
        "spot_bid_price_percent": "spotBidPricePercent",
        "zone_id": "zoneId",
    },
)
class DataDatabricksClusterClusterInfoAwsAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__060687017a6683f4c7f78822b15c7edf71b45e792e6249e9114a0bd28c23aa44)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument ebs_volume_count", value=ebs_volume_count, expected_type=type_hints["ebs_volume_count"])
            check_type(argname="argument ebs_volume_iops", value=ebs_volume_iops, expected_type=type_hints["ebs_volume_iops"])
            check_type(argname="argument ebs_volume_size", value=ebs_volume_size, expected_type=type_hints["ebs_volume_size"])
            check_type(argname="argument ebs_volume_throughput", value=ebs_volume_throughput, expected_type=type_hints["ebs_volume_throughput"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument spot_bid_price_percent", value=spot_bid_price_percent, expected_type=type_hints["spot_bid_price_percent"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if ebs_volume_count is not None:
            self._values["ebs_volume_count"] = ebs_volume_count
        if ebs_volume_iops is not None:
            self._values["ebs_volume_iops"] = ebs_volume_iops
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if ebs_volume_throughput is not None:
            self._values["ebs_volume_throughput"] = ebs_volume_throughput
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if spot_bid_price_percent is not None:
            self._values["spot_bid_price_percent"] = spot_bid_price_percent
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.'''
        result = self._values.get("ebs_volume_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.'''
        result = self._values.get("ebs_volume_iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.'''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.'''
        result = self._values.get("ebs_volume_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.'''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_price_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.'''
        result = self._values.get("spot_bid_price_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f81ba997844101640d70c2697e7cc6abfa14535428a19fbd5a364455c84ff89c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetEbsVolumeCount")
    def reset_ebs_volume_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeCount", []))

    @jsii.member(jsii_name="resetEbsVolumeIops")
    def reset_ebs_volume_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeIops", []))

    @jsii.member(jsii_name="resetEbsVolumeSize")
    def reset_ebs_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeSize", []))

    @jsii.member(jsii_name="resetEbsVolumeThroughput")
    def reset_ebs_volume_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeThroughput", []))

    @jsii.member(jsii_name="resetEbsVolumeType")
    def reset_ebs_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeType", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

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
    @jsii.member(jsii_name="ebsVolumeCountInput")
    def ebs_volume_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIopsInput")
    def ebs_volume_iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeIopsInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSizeInput")
    def ebs_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughputInput")
    def ebs_volume_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeTypeInput")
    def ebs_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ebsVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__970f4adf30aee8f77e0e6d817564d02f6641dc9b044f98726f732589738de46c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeCount")
    def ebs_volume_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeCount"))

    @ebs_volume_count.setter
    def ebs_volume_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa4323aea0be122647bb06a0285e94de2af7992410275f13bf6796e85eebd915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIops")
    def ebs_volume_iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeIops"))

    @ebs_volume_iops.setter
    def ebs_volume_iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eba9f9990fdbb1a179d2285d80453b5a2f416cb705d7bf24b3784bda759d8d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeIops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSize")
    def ebs_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeSize"))

    @ebs_volume_size.setter
    def ebs_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc009aa4886cd3b1ee07a4bb78e804a0c7030fb8ce68e0dbf3193e04ecda199)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughput")
    def ebs_volume_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeThroughput"))

    @ebs_volume_throughput.setter
    def ebs_volume_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba748dc3c78f2e79400a1429570fcbb7a73d24771ac0ed343fe98fe273ff85c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeType")
    def ebs_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ebsVolumeType"))

    @ebs_volume_type.setter
    def ebs_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b6140b00e2942864335c6191127f33cf6b842e08ee35641cbd1763ec98c33e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b796f7ee77bd1bed67214cd1ac7faf229537b451e335ea182249ff6c28bf701f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e850214790cae037d58a4842aca1cea1fb0e6fd882aa56bab20c45c3a32a574c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercent")
    def spot_bid_price_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidPricePercent"))

    @spot_bid_price_percent.setter
    def spot_bid_price_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5882a8b5ec4aee904787873dec8524946e1ef601968589355ad1d033835f5b5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidPricePercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd2c3108d6f2222e31260a3f70143204c9398825bae67dd37da38f9b2041d683)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd26067baedf055eb6b688c456c4f12e95331dc5caf70f9d03a291927f99fcbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAzureAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "first_on_demand": "firstOnDemand",
        "log_analytics_info": "logAnalyticsInfo",
        "spot_bid_max_price": "spotBidMaxPrice",
    },
)
class DataDatabricksClusterClusterInfoAzureAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.
        '''
        if isinstance(log_analytics_info, dict):
            log_analytics_info = DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo(**log_analytics_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec36542822dccc27e818d16be714f69c4d1671962cbc195c82c6a8c2f4c0898)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument log_analytics_info", value=log_analytics_info, expected_type=type_hints["log_analytics_info"])
            check_type(argname="argument spot_bid_max_price", value=spot_bid_max_price, expected_type=type_hints["spot_bid_max_price"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if log_analytics_info is not None:
            self._values["log_analytics_info"] = log_analytics_info
        if spot_bid_max_price is not None:
            self._values["spot_bid_max_price"] = spot_bid_max_price

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_analytics_info(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo"]:
        '''log_analytics_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        '''
        result = self._values.get("log_analytics_info")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo"], result)

    @builtins.property
    def spot_bid_max_price(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.'''
        result = self._values.get("spot_bid_max_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoAzureAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo",
    jsii_struct_bases=[],
    name_mapping={
        "log_analytics_primary_key": "logAnalyticsPrimaryKey",
        "log_analytics_workspace_id": "logAnalyticsWorkspaceId",
    },
)
class DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo:
    def __init__(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a2946db0de955bc04b2b2a53da4db21aafdcfa008d2bc69e78d8040c29b29c)
            check_type(argname="argument log_analytics_primary_key", value=log_analytics_primary_key, expected_type=type_hints["log_analytics_primary_key"])
            check_type(argname="argument log_analytics_workspace_id", value=log_analytics_workspace_id, expected_type=type_hints["log_analytics_workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_analytics_primary_key is not None:
            self._values["log_analytics_primary_key"] = log_analytics_primary_key
        if log_analytics_workspace_id is not None:
            self._values["log_analytics_workspace_id"] = log_analytics_workspace_id

    @builtins.property
    def log_analytics_primary_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.'''
        result = self._values.get("log_analytics_primary_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_analytics_workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.'''
        result = self._values.get("log_analytics_workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94d2e3dbc3ccd24b9da490b8da4917dcdf843944f3148430d9bf4d851e095205)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLogAnalyticsPrimaryKey")
    def reset_log_analytics_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsPrimaryKey", []))

    @jsii.member(jsii_name="resetLogAnalyticsWorkspaceId")
    def reset_log_analytics_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKeyInput")
    def log_analytics_primary_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsPrimaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceIdInput")
    def log_analytics_workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsWorkspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKey")
    def log_analytics_primary_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsPrimaryKey"))

    @log_analytics_primary_key.setter
    def log_analytics_primary_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce148e5a0f57eeb3a89ef8dede0bff9c564bde5c238af89c48d3f599b00a175)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsPrimaryKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceId")
    def log_analytics_workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsWorkspaceId"))

    @log_analytics_workspace_id.setter
    def log_analytics_workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0835188fbcc4809a7826a8aa136569e75869bf124d5980769a34198e2b765bce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c94723209830e8be1b3e7045f809f349f0f635e7d96142faa90d15dcfa13ba8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoAzureAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoAzureAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3c8cd141c27b2c2d846117e13a084afe4de0adb973d2c1a1ffae84582aea867)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLogAnalyticsInfo")
    def put_log_analytics_info(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.
        '''
        value = DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo(
            log_analytics_primary_key=log_analytics_primary_key,
            log_analytics_workspace_id=log_analytics_workspace_id,
        )

        return typing.cast(None, jsii.invoke(self, "putLogAnalyticsInfo", [value]))

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetLogAnalyticsInfo")
    def reset_log_analytics_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsInfo", []))

    @jsii.member(jsii_name="resetSpotBidMaxPrice")
    def reset_spot_bid_max_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidMaxPrice", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfo")
    def log_analytics_info(
        self,
    ) -> DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfoOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfoOutputReference, jsii.get(self, "logAnalyticsInfo"))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfoInput")
    def log_analytics_info_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo], jsii.get(self, "logAnalyticsInfoInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__6424770ffe309b2b0596e3133a285f97f9cc34fb8becf973de311bf538b81b06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__437e341f232c0196c3231119587bd7731d1cd35bb6942685b698b2199678905d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPrice")
    def spot_bid_max_price(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidMaxPrice"))

    @spot_bid_max_price.setter
    def spot_bid_max_price(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd728ef2f2d7c0aea03746777640d078ca7844dc757c2310a3580c4f35a683f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidMaxPrice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7384228cb2140c413611389d532bdd60910faa170bf821e2f4510f803dda64c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConf",
    jsii_struct_bases=[],
    name_mapping={"dbfs": "dbfs", "s3": "s3", "volumes": "volumes"},
)
class DataDatabricksClusterClusterInfoClusterLogConf:
    def __init__(
        self,
        *,
        dbfs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogConfDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogConfS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoClusterLogConfVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        if isinstance(dbfs, dict):
            dbfs = DataDatabricksClusterClusterInfoClusterLogConfDbfs(**dbfs)
        if isinstance(s3, dict):
            s3 = DataDatabricksClusterClusterInfoClusterLogConfS3(**s3)
        if isinstance(volumes, dict):
            volumes = DataDatabricksClusterClusterInfoClusterLogConfVolumes(**volumes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__451a0c7c98565e47235d6e74d8b7df3a27673c5b4ca678ef26a4fa85f482d840)
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def dbfs(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfDbfs"], result)

    @builtins.property
    def s3(self) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfS3"], result)

    @builtins.property
    def volumes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfVolumes"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoClusterLogConf(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoClusterLogConfDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c94e315810d4fa1309fd5dec46d327742f2d4085d58f8cb903a5a494c4ddf37)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoClusterLogConfDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoClusterLogConfDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07825f2e9284d1ca8e150d5afb12188fbb5125d2fbcc670814e0f62cb24fa46d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__081580da1789e207814624e3b17cfbc036ec41532b1d044cd41ce3e61e55a148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29310c16851df40418ad05d40fd87fbf755255521e34b4dba84643d3f70cc7e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoClusterLogConfOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2f5bba261ec9a275ca87196a5f385380ba15d0028a7a1aecc19a58850136a59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoClusterLogConfDbfs(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        value = DataDatabricksClusterClusterInfoClusterLogConfS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoClusterLogConfVolumes(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(self) -> DataDatabricksClusterClusterInfoClusterLogConfDbfsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoClusterLogConfDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(self) -> "DataDatabricksClusterClusterInfoClusterLogConfS3OutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoClusterLogConfS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(
        self,
    ) -> "DataDatabricksClusterClusterInfoClusterLogConfVolumesOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoClusterLogConfVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfS3"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfVolumes"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoClusterLogConfVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d81804f6a7c21bfef2b0e11931361538d05ea1c9ed713de3438b51ea675997b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class DataDatabricksClusterClusterInfoClusterLogConfS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20a2a7d01952ab164f7d87d0bdc7769de04513a471d6140efabf33dc3da46064)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoClusterLogConfS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoClusterLogConfS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__06131481b14249278ca738634899d5f1aee5b331e334cfc5c48f8e3b894130bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f00b1c1ed199eead343b576ac29a3e0e8eaace9d3cbcbc2f2eb9166f38b7d88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3109fbd61353ab7c9c73f5e31f36a2a40d764e9d09c42f0bebb71f2e52fe065b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36e56a73067a73d1016168b1f098162c69b3eebeb003c0dc61e346a9e6cab188)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8177e776b121dc504a45757a3336701af5a48e9806c4f483985d3faac7d86bd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__407842af49d6404da7b4553f4126f123d749691f92f2e6c5cb2c03c728eb700f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__869a15040243a0463170f8060ae98b7d6908ec237afb7d1dacaa4f60339a82ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a4977fc0bfa4a03a4a53921b1e36b2c3858028174c02bf48c49897cdb00061e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfS3]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d86bf06b7f50dda5d2103bf087b9ba2529c4d8a880829f264a968d944dde5f67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoClusterLogConfVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e90624a2c8601efd03da3b11dc645f55f646d9f8bfd246785b305793af1bb6eb)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoClusterLogConfVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoClusterLogConfVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogConfVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb22a8ff0ad2cc8dc5b2d255e1f3d64bca2d6bb95a2b1d4e9d852c549bae44c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e32ed85d2b0cc28288d57fd0fb6709ed2a8c594f3ac11ab6a21588ada7f1e163)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfVolumes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c74adcb7f68c12a967d0f454d09b91b2f15d0b7e6ff9adf2d1cbae06c2000aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogStatus",
    jsii_struct_bases=[],
    name_mapping={
        "last_attempted": "lastAttempted",
        "last_exception": "lastException",
    },
)
class DataDatabricksClusterClusterInfoClusterLogStatus:
    def __init__(
        self,
        *,
        last_attempted: typing.Optional[jsii.Number] = None,
        last_exception: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param last_attempted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_attempted DataDatabricksCluster#last_attempted}.
        :param last_exception: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_exception DataDatabricksCluster#last_exception}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06eeb3670b53e443ccf228f492206924ef7cb9d635763a487922dc8c29ab499b)
            check_type(argname="argument last_attempted", value=last_attempted, expected_type=type_hints["last_attempted"])
            check_type(argname="argument last_exception", value=last_exception, expected_type=type_hints["last_exception"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if last_attempted is not None:
            self._values["last_attempted"] = last_attempted
        if last_exception is not None:
            self._values["last_exception"] = last_exception

    @builtins.property
    def last_attempted(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_attempted DataDatabricksCluster#last_attempted}.'''
        result = self._values.get("last_attempted")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def last_exception(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_exception DataDatabricksCluster#last_exception}.'''
        result = self._values.get("last_exception")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoClusterLogStatus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoClusterLogStatusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoClusterLogStatusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6aadd2ed8a3715c1520c7488e955f04daceb0c20d323f34068ce4ce693f50eaf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLastAttempted")
    def reset_last_attempted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastAttempted", []))

    @jsii.member(jsii_name="resetLastException")
    def reset_last_exception(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastException", []))

    @builtins.property
    @jsii.member(jsii_name="lastAttemptedInput")
    def last_attempted_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastAttemptedInput"))

    @builtins.property
    @jsii.member(jsii_name="lastExceptionInput")
    def last_exception_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastExceptionInput"))

    @builtins.property
    @jsii.member(jsii_name="lastAttempted")
    def last_attempted(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastAttempted"))

    @last_attempted.setter
    def last_attempted(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__583222fcf9d9569f58e7eef639cca9e138348f024b6a611c227c8d97c45c2eb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastAttempted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastException")
    def last_exception(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastException"))

    @last_exception.setter
    def last_exception(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b37043262f004f19a42be3f013b4dee4411fbacd9b09a65c78468bd07bdf309b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastException", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf21fd1ca134e80581ef285c950289788e8e8ede383ce2ec0583d203711f1a18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDockerImage",
    jsii_struct_bases=[],
    name_mapping={"basic_auth": "basicAuth", "url": "url"},
)
class DataDatabricksClusterClusterInfoDockerImage:
    def __init__(
        self,
        *,
        basic_auth: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDockerImageBasicAuth", typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.
        '''
        if isinstance(basic_auth, dict):
            basic_auth = DataDatabricksClusterClusterInfoDockerImageBasicAuth(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dfbaa9d7aa202bcc8a3aa88db3acb8adcf55e3affad038966e42a54f8a3f953)
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def basic_auth(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoDockerImageBasicAuth"]:
        '''basic_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoDockerImageBasicAuth"], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoDockerImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDockerImageBasicAuth",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class DataDatabricksClusterClusterInfoDockerImageBasicAuth:
    def __init__(
        self,
        *,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__761b360360d2ab65569cc14de4c4c9c4f717740017d648342b5e6fb63dd4e09c)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoDockerImageBasicAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoDockerImageBasicAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDockerImageBasicAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b19c8260c8e15473c09850b67e8e8287922bf30d63be715bee653d6540c91492)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__32cb61c3b2556c2d374a33a1ecb04e9e757092b3bec8b0bcf2b7c71cadd02155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c781b02d8b4f5df06440507923978efc3f4724b0afa44b8693fb51a8bdeb7fe3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07eb9eb22b21828dd8f083e769e7963f340d7b1c6d3b2e40d99291297668ba9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoDockerImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDockerImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__334c4508d85bb7cb0ad8ddaa500f071d805b42cf609576815edcba98247b585f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBasicAuth")
    def put_basic_auth(
        self,
        *,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.
        '''
        value = DataDatabricksClusterClusterInfoDockerImageBasicAuth(
            password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putBasicAuth", [value]))

    @jsii.member(jsii_name="resetBasicAuth")
    def reset_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuth", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @builtins.property
    @jsii.member(jsii_name="basicAuth")
    def basic_auth(
        self,
    ) -> DataDatabricksClusterClusterInfoDockerImageBasicAuthOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoDockerImageBasicAuthOutputReference, jsii.get(self, "basicAuth"))

    @builtins.property
    @jsii.member(jsii_name="basicAuthInput")
    def basic_auth_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth], jsii.get(self, "basicAuthInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__12f2e2b7c8aa32dbdd3f65ad24a74bd9b07d85e1939f30ada93a03bac74b01ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDockerImage]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDockerImage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoDockerImage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__928b91e38802299174dfb1a813070bd8711d9f10a88ceac8209ff59f40f46f3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDriver",
    jsii_struct_bases=[],
    name_mapping={
        "host_private_ip": "hostPrivateIp",
        "instance_id": "instanceId",
        "node_aws_attributes": "nodeAwsAttributes",
        "node_id": "nodeId",
        "private_ip": "privateIp",
        "public_dns": "publicDns",
        "start_timestamp": "startTimestamp",
    },
)
class DataDatabricksClusterClusterInfoDriver:
    def __init__(
        self,
        *,
        host_private_ip: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        node_aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoDriverNodeAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        node_id: typing.Optional[builtins.str] = None,
        private_ip: typing.Optional[builtins.str] = None,
        public_dns: typing.Optional[builtins.str] = None,
        start_timestamp: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param host_private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#host_private_ip DataDatabricksCluster#host_private_ip}.
        :param instance_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_id DataDatabricksCluster#instance_id}.
        :param node_aws_attributes: node_aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_aws_attributes DataDatabricksCluster#node_aws_attributes}
        :param node_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_id DataDatabricksCluster#node_id}.
        :param private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#private_ip DataDatabricksCluster#private_ip}.
        :param public_dns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#public_dns DataDatabricksCluster#public_dns}.
        :param start_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_timestamp DataDatabricksCluster#start_timestamp}.
        '''
        if isinstance(node_aws_attributes, dict):
            node_aws_attributes = DataDatabricksClusterClusterInfoDriverNodeAwsAttributes(**node_aws_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93d8d212082c22fe59b0dc2b07716ae7e3d544e4b77399dfdcee1f09cb003495)
            check_type(argname="argument host_private_ip", value=host_private_ip, expected_type=type_hints["host_private_ip"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument node_aws_attributes", value=node_aws_attributes, expected_type=type_hints["node_aws_attributes"])
            check_type(argname="argument node_id", value=node_id, expected_type=type_hints["node_id"])
            check_type(argname="argument private_ip", value=private_ip, expected_type=type_hints["private_ip"])
            check_type(argname="argument public_dns", value=public_dns, expected_type=type_hints["public_dns"])
            check_type(argname="argument start_timestamp", value=start_timestamp, expected_type=type_hints["start_timestamp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host_private_ip is not None:
            self._values["host_private_ip"] = host_private_ip
        if instance_id is not None:
            self._values["instance_id"] = instance_id
        if node_aws_attributes is not None:
            self._values["node_aws_attributes"] = node_aws_attributes
        if node_id is not None:
            self._values["node_id"] = node_id
        if private_ip is not None:
            self._values["private_ip"] = private_ip
        if public_dns is not None:
            self._values["public_dns"] = public_dns
        if start_timestamp is not None:
            self._values["start_timestamp"] = start_timestamp

    @builtins.property
    def host_private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#host_private_ip DataDatabricksCluster#host_private_ip}.'''
        result = self._values.get("host_private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_id DataDatabricksCluster#instance_id}.'''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_aws_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoDriverNodeAwsAttributes"]:
        '''node_aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_aws_attributes DataDatabricksCluster#node_aws_attributes}
        '''
        result = self._values.get("node_aws_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoDriverNodeAwsAttributes"], result)

    @builtins.property
    def node_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_id DataDatabricksCluster#node_id}.'''
        result = self._values.get("node_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#private_ip DataDatabricksCluster#private_ip}.'''
        result = self._values.get("private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_dns(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#public_dns DataDatabricksCluster#public_dns}.'''
        result = self._values.get("public_dns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_timestamp(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_timestamp DataDatabricksCluster#start_timestamp}.'''
        result = self._values.get("start_timestamp")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoDriver(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDriverNodeAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={"is_spot": "isSpot"},
)
class DataDatabricksClusterClusterInfoDriverNodeAwsAttributes:
    def __init__(
        self,
        *,
        is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09872ab0283a84c409df67e91d2316d1b5d3eaae51d0db90897561ae1a41d24)
            check_type(argname="argument is_spot", value=is_spot, expected_type=type_hints["is_spot"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_spot is not None:
            self._values["is_spot"] = is_spot

    @builtins.property
    def is_spot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.'''
        result = self._values.get("is_spot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoDriverNodeAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoDriverNodeAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDriverNodeAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c37ffb02f798d989938f533b51690208d4ab02fe50b00dcbfadfd9b1932af3a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsSpot")
    def reset_is_spot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSpot", []))

    @builtins.property
    @jsii.member(jsii_name="isSpotInput")
    def is_spot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="isSpot")
    def is_spot(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSpot"))

    @is_spot.setter
    def is_spot(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51f1ac2146b5423809e5619e9e85bff0c8a2c572440ba3faefd9bba6b5750520)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSpot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024693618d340fd40b6470e408ceda0f1ebe2ec8120a8f028da5dd2857662b36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoDriverOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoDriverOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c29e03d20b78011fdf7121f78aae8f82946665c67d44b13c1320a4e9bacb302)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNodeAwsAttributes")
    def put_node_aws_attributes(
        self,
        *,
        is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.
        '''
        value = DataDatabricksClusterClusterInfoDriverNodeAwsAttributes(
            is_spot=is_spot
        )

        return typing.cast(None, jsii.invoke(self, "putNodeAwsAttributes", [value]))

    @jsii.member(jsii_name="resetHostPrivateIp")
    def reset_host_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostPrivateIp", []))

    @jsii.member(jsii_name="resetInstanceId")
    def reset_instance_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceId", []))

    @jsii.member(jsii_name="resetNodeAwsAttributes")
    def reset_node_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeAwsAttributes", []))

    @jsii.member(jsii_name="resetNodeId")
    def reset_node_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeId", []))

    @jsii.member(jsii_name="resetPrivateIp")
    def reset_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIp", []))

    @jsii.member(jsii_name="resetPublicDns")
    def reset_public_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicDns", []))

    @jsii.member(jsii_name="resetStartTimestamp")
    def reset_start_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTimestamp", []))

    @builtins.property
    @jsii.member(jsii_name="nodeAwsAttributes")
    def node_aws_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoDriverNodeAwsAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoDriverNodeAwsAttributesOutputReference, jsii.get(self, "nodeAwsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="hostPrivateIpInput")
    def host_private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostPrivateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeAwsAttributesInput")
    def node_aws_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes], jsii.get(self, "nodeAwsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeIdInput")
    def node_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpInput")
    def private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="publicDnsInput")
    def public_dns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="startTimestampInput")
    def start_timestamp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="hostPrivateIp")
    def host_private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostPrivateIp"))

    @host_private_ip.setter
    def host_private_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde72e430cb3a61e8e71b9a31745a7526f13eb8d2912794722626b3d3ec45a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostPrivateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca0440698826da0d2ac51093146016942cd1e3d647091d46c2f89d61218e5e93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @node_id.setter
    def node_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32da65206da6c7035041e62f70e14f0a695da880430f9e9d864c4244d6605ec6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIp")
    def private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIp"))

    @private_ip.setter
    def private_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3586f5c9abe693664abec246aaba325b24bb402704972844829f16969059e090)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicDns")
    def public_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicDns"))

    @public_dns.setter
    def public_dns(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6d900b1919d61519f6ba03d4d6a965fbd45cab554f85179654cd5f60d00e02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTimestamp")
    def start_timestamp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startTimestamp"))

    @start_timestamp.setter
    def start_timestamp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7b76ad4f2df6d8f724ab48ff6954a93ce30217e4ddd54e072be81fc43fe600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksClusterClusterInfoDriver]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDriver], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoDriver],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__413aa894dd397a7d674d5ac2d68e63dced2a665ebc0b2abe2fcea6dc9f458fa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoExecutors",
    jsii_struct_bases=[],
    name_mapping={
        "host_private_ip": "hostPrivateIp",
        "instance_id": "instanceId",
        "node_aws_attributes": "nodeAwsAttributes",
        "node_id": "nodeId",
        "private_ip": "privateIp",
        "public_dns": "publicDns",
        "start_timestamp": "startTimestamp",
    },
)
class DataDatabricksClusterClusterInfoExecutors:
    def __init__(
        self,
        *,
        host_private_ip: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        node_aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        node_id: typing.Optional[builtins.str] = None,
        private_ip: typing.Optional[builtins.str] = None,
        public_dns: typing.Optional[builtins.str] = None,
        start_timestamp: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param host_private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#host_private_ip DataDatabricksCluster#host_private_ip}.
        :param instance_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_id DataDatabricksCluster#instance_id}.
        :param node_aws_attributes: node_aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_aws_attributes DataDatabricksCluster#node_aws_attributes}
        :param node_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_id DataDatabricksCluster#node_id}.
        :param private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#private_ip DataDatabricksCluster#private_ip}.
        :param public_dns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#public_dns DataDatabricksCluster#public_dns}.
        :param start_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_timestamp DataDatabricksCluster#start_timestamp}.
        '''
        if isinstance(node_aws_attributes, dict):
            node_aws_attributes = DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes(**node_aws_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68ced940de52b31db12815d33e7cb6bca0a631385e40a83f80940ddf1c04a861)
            check_type(argname="argument host_private_ip", value=host_private_ip, expected_type=type_hints["host_private_ip"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument node_aws_attributes", value=node_aws_attributes, expected_type=type_hints["node_aws_attributes"])
            check_type(argname="argument node_id", value=node_id, expected_type=type_hints["node_id"])
            check_type(argname="argument private_ip", value=private_ip, expected_type=type_hints["private_ip"])
            check_type(argname="argument public_dns", value=public_dns, expected_type=type_hints["public_dns"])
            check_type(argname="argument start_timestamp", value=start_timestamp, expected_type=type_hints["start_timestamp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host_private_ip is not None:
            self._values["host_private_ip"] = host_private_ip
        if instance_id is not None:
            self._values["instance_id"] = instance_id
        if node_aws_attributes is not None:
            self._values["node_aws_attributes"] = node_aws_attributes
        if node_id is not None:
            self._values["node_id"] = node_id
        if private_ip is not None:
            self._values["private_ip"] = private_ip
        if public_dns is not None:
            self._values["public_dns"] = public_dns
        if start_timestamp is not None:
            self._values["start_timestamp"] = start_timestamp

    @builtins.property
    def host_private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#host_private_ip DataDatabricksCluster#host_private_ip}.'''
        result = self._values.get("host_private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_id DataDatabricksCluster#instance_id}.'''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_aws_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes"]:
        '''node_aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_aws_attributes DataDatabricksCluster#node_aws_attributes}
        '''
        result = self._values.get("node_aws_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes"], result)

    @builtins.property
    def node_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_id DataDatabricksCluster#node_id}.'''
        result = self._values.get("node_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#private_ip DataDatabricksCluster#private_ip}.'''
        result = self._values.get("private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_dns(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#public_dns DataDatabricksCluster#public_dns}.'''
        result = self._values.get("public_dns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_timestamp(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_timestamp DataDatabricksCluster#start_timestamp}.'''
        result = self._values.get("start_timestamp")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoExecutors(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoExecutorsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoExecutorsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7bd3aa065b6d5e534326758510259e2d950aa996aeb5d2501b88c9081bec549)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksClusterClusterInfoExecutorsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1a3fdbfa2f18fe2275334a1f3878050cba03a7acf573bf3f4172092b71cd639)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksClusterClusterInfoExecutorsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e2fbb17f19c1b0972057ee7810e71b2da1609f8034fcf9e86e46157f878b60)
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
            type_hints = typing.get_type_hints(_typecheckingstub__578633b5dc86ecaee9997001abb099125ac498a297889551b6cf384a5f420a88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__08ba83c29cc5dae5d8337b607c115779b090527175ee6f894305984d436ecf96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f75cd622b98d119eba41bd5a7e0746da030f23d7b4a744cbbcf2a8c47b58c29a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={"is_spot": "isSpot"},
)
class DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes:
    def __init__(
        self,
        *,
        is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea4fd17208a88155a5a8030d28ccd234937e79ee10760a1eacd8d8b64ecac61c)
            check_type(argname="argument is_spot", value=is_spot, expected_type=type_hints["is_spot"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_spot is not None:
            self._values["is_spot"] = is_spot

    @builtins.property
    def is_spot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.'''
        result = self._values.get("is_spot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b51a2a53f182bb38c9341a462531fc37088c69f56b614c28e9eaea85c0c676ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsSpot")
    def reset_is_spot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSpot", []))

    @builtins.property
    @jsii.member(jsii_name="isSpotInput")
    def is_spot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="isSpot")
    def is_spot(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSpot"))

    @is_spot.setter
    def is_spot(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e933cb9af7cc5bf6388d45ba04942e1604a145abf869e03057589720f65ed044)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSpot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfe1cf24479428185d3d3d9816adb271579f8fa4a73a4908067b4a43417b47c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoExecutorsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoExecutorsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__794e44d680e36d45e3f9ad57a343dbb3667b313026f04670a5983843a2040da3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNodeAwsAttributes")
    def put_node_aws_attributes(
        self,
        *,
        is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_spot DataDatabricksCluster#is_spot}.
        '''
        value = DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes(
            is_spot=is_spot
        )

        return typing.cast(None, jsii.invoke(self, "putNodeAwsAttributes", [value]))

    @jsii.member(jsii_name="resetHostPrivateIp")
    def reset_host_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostPrivateIp", []))

    @jsii.member(jsii_name="resetInstanceId")
    def reset_instance_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceId", []))

    @jsii.member(jsii_name="resetNodeAwsAttributes")
    def reset_node_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeAwsAttributes", []))

    @jsii.member(jsii_name="resetNodeId")
    def reset_node_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeId", []))

    @jsii.member(jsii_name="resetPrivateIp")
    def reset_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIp", []))

    @jsii.member(jsii_name="resetPublicDns")
    def reset_public_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicDns", []))

    @jsii.member(jsii_name="resetStartTimestamp")
    def reset_start_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTimestamp", []))

    @builtins.property
    @jsii.member(jsii_name="nodeAwsAttributes")
    def node_aws_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributesOutputReference, jsii.get(self, "nodeAwsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="hostPrivateIpInput")
    def host_private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostPrivateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeAwsAttributesInput")
    def node_aws_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes], jsii.get(self, "nodeAwsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeIdInput")
    def node_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpInput")
    def private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="publicDnsInput")
    def public_dns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="startTimestampInput")
    def start_timestamp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="hostPrivateIp")
    def host_private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostPrivateIp"))

    @host_private_ip.setter
    def host_private_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a59ddda92d58e03b9020b80a222d7d1b6b0ea137f918608fe3efaebf269763a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostPrivateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49b9ffc3075332a8dc11936c90b574c720e172a74ca47711774f14207b814c9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @node_id.setter
    def node_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5465a4e0196e45c63f04569c23cd7bf9754d05d42e1c8c2351433aca95d32196)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIp")
    def private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIp"))

    @private_ip.setter
    def private_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ac1b67608952025fc443fc8b4783edcd5902a8685be001d1961b0212d9a2616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicDns")
    def public_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicDns"))

    @public_dns.setter
    def public_dns(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc3109f80bb63adf9b3a969f529f050cb93b7b5c40cfb7994851e65c6b5a58c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTimestamp")
    def start_timestamp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startTimestamp"))

    @start_timestamp.setter
    def start_timestamp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d700fbfb34a8b44c99bb388afbb3a51849ee8cd93abbf63ce4c450ec10bb8bfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoExecutors]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoExecutors]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoExecutors]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63620a0f204d78f9e67fcf784f90bc6904678d678e7b7d13dc6e68363a855b2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoGcpAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "boot_disk_size": "bootDiskSize",
        "first_on_demand": "firstOnDemand",
        "google_service_account": "googleServiceAccount",
        "local_ssd_count": "localSsdCount",
        "use_preemptible_executors": "usePreemptibleExecutors",
        "zone_id": "zoneId",
    },
)
class DataDatabricksClusterClusterInfoGcpAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        boot_disk_size: typing.Optional[jsii.Number] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param boot_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.
        :param use_preemptible_executors: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85df097f450b27adaa3edd52f3d9beb9ccd2aaa8d69e14dc607a5b8fa3294cc3)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument boot_disk_size", value=boot_disk_size, expected_type=type_hints["boot_disk_size"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument google_service_account", value=google_service_account, expected_type=type_hints["google_service_account"])
            check_type(argname="argument local_ssd_count", value=local_ssd_count, expected_type=type_hints["local_ssd_count"])
            check_type(argname="argument use_preemptible_executors", value=use_preemptible_executors, expected_type=type_hints["use_preemptible_executors"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if boot_disk_size is not None:
            self._values["boot_disk_size"] = boot_disk_size
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if google_service_account is not None:
            self._values["google_service_account"] = google_service_account
        if local_ssd_count is not None:
            self._values["local_ssd_count"] = local_ssd_count
        if use_preemptible_executors is not None:
            self._values["use_preemptible_executors"] = use_preemptible_executors
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def boot_disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.'''
        result = self._values.get("boot_disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def google_service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.'''
        result = self._values.get("google_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def use_preemptible_executors(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.'''
        result = self._values.get("use_preemptible_executors")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoGcpAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoGcpAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoGcpAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b5ea7dea4b4d797090941398d6e37fe06fb757f70ec9b49738262c1250dd791)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetBootDiskSize")
    def reset_boot_disk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDiskSize", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetGoogleServiceAccount")
    def reset_google_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleServiceAccount", []))

    @jsii.member(jsii_name="resetLocalSsdCount")
    def reset_local_ssd_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSsdCount", []))

    @jsii.member(jsii_name="resetUsePreemptibleExecutors")
    def reset_use_preemptible_executors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePreemptibleExecutors", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDiskSizeInput")
    def boot_disk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bootDiskSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccountInput")
    def google_service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="localSsdCountInput")
    def local_ssd_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localSsdCountInput"))

    @builtins.property
    @jsii.member(jsii_name="usePreemptibleExecutorsInput")
    def use_preemptible_executors_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePreemptibleExecutorsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__df804ebf4b5c81cd88762d5f58e8e94d70e965d7cccbb6a83ffd40852d1b42be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootDiskSize")
    def boot_disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootDiskSize"))

    @boot_disk_size.setter
    def boot_disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d369c4a4894a5986f367a8d9ddc89ffec379c6a01d84960dba8f31636f1b55ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootDiskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__570627fc8ab2c5f472c7fb053e3551c75ca437434a212058ce36d434183da550)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccount")
    def google_service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "googleServiceAccount"))

    @google_service_account.setter
    def google_service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f2daf34b1b8730a16da7586ef1f70bddb52054b9128cd825a49a4b794da4f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleServiceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cadccf360d499e9e77a0361aa3b342374d7cb001aeaee850cd94898936c92be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePreemptibleExecutors")
    def use_preemptible_executors(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePreemptibleExecutors"))

    @use_preemptible_executors.setter
    def use_preemptible_executors(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cc0389609f43b79c8a61bd119ebb3ac1b108126603410c0bfca31eb4feadce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePreemptibleExecutors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79c663ae159db23aad58c80629cb05607779c3fc6a415c7bdcab68c700caf7b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15bf4d4d97a125c1039e84ea00a60b4fb7a110154849228f6f1aaae9ccf17f09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScripts",
    jsii_struct_bases=[],
    name_mapping={
        "abfss": "abfss",
        "dbfs": "dbfs",
        "file": "file",
        "gcs": "gcs",
        "s3": "s3",
        "volumes": "volumes",
        "workspace": "workspace",
    },
)
class DataDatabricksClusterClusterInfoInitScripts:
    def __init__(
        self,
        *,
        abfss: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsAbfss", typing.Dict[builtins.str, typing.Any]]] = None,
        dbfs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        file: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsFile", typing.Dict[builtins.str, typing.Any]]] = None,
        gcs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsGcs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoInitScriptsWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param abfss: abfss block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#abfss DataDatabricksCluster#abfss}
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param file: file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#file DataDatabricksCluster#file}
        :param gcs: gcs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcs DataDatabricksCluster#gcs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        :param workspace: workspace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workspace DataDatabricksCluster#workspace}
        '''
        if isinstance(abfss, dict):
            abfss = DataDatabricksClusterClusterInfoInitScriptsAbfss(**abfss)
        if isinstance(dbfs, dict):
            dbfs = DataDatabricksClusterClusterInfoInitScriptsDbfs(**dbfs)
        if isinstance(file, dict):
            file = DataDatabricksClusterClusterInfoInitScriptsFile(**file)
        if isinstance(gcs, dict):
            gcs = DataDatabricksClusterClusterInfoInitScriptsGcs(**gcs)
        if isinstance(s3, dict):
            s3 = DataDatabricksClusterClusterInfoInitScriptsS3(**s3)
        if isinstance(volumes, dict):
            volumes = DataDatabricksClusterClusterInfoInitScriptsVolumes(**volumes)
        if isinstance(workspace, dict):
            workspace = DataDatabricksClusterClusterInfoInitScriptsWorkspace(**workspace)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec251c56f5f0ef33a2270f603e47796ff276953e777a2c2cf10fd5ca203f6d3)
            check_type(argname="argument abfss", value=abfss, expected_type=type_hints["abfss"])
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument gcs", value=gcs, expected_type=type_hints["gcs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
            check_type(argname="argument workspace", value=workspace, expected_type=type_hints["workspace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if abfss is not None:
            self._values["abfss"] = abfss
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if file is not None:
            self._values["file"] = file
        if gcs is not None:
            self._values["gcs"] = gcs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes
        if workspace is not None:
            self._values["workspace"] = workspace

    @builtins.property
    def abfss(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsAbfss"]:
        '''abfss block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#abfss DataDatabricksCluster#abfss}
        '''
        result = self._values.get("abfss")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsAbfss"], result)

    @builtins.property
    def dbfs(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsDbfs"], result)

    @builtins.property
    def file(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsFile"]:
        '''file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#file DataDatabricksCluster#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsFile"], result)

    @builtins.property
    def gcs(self) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsGcs"]:
        '''gcs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcs DataDatabricksCluster#gcs}
        '''
        result = self._values.get("gcs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsGcs"], result)

    @builtins.property
    def s3(self) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsS3"], result)

    @builtins.property
    def volumes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsVolumes"], result)

    @builtins.property
    def workspace(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsWorkspace"]:
        '''workspace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workspace DataDatabricksCluster#workspace}
        '''
        result = self._values.get("workspace")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsWorkspace"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScripts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsAbfss",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsAbfss:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea52d24a26a99bb2d548e021e8013a737945380c3d5e4447069818bbde511d5)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsAbfss(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsAbfssOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsAbfssOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__84a8509d164f3550fb296dbfbef0d8b33c90593377d7667998c82dc0ec767bc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf5f65a506056abb7d7378e596d10a75039fa89eb4e64ad32048b7623a5413c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82e9d562c80036b5c0c9f22071f2e546d1df5acec902074629708c098e574e44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d67109009094a4deab6e1d4b67f58a1b9ae50f97003149acd85746b67868fe30)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81631ac7e39fe2dcc22e09cf1981897487152fbea5e8d1b1ff09f7bf07e9f9d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ff45f4409a7c97daa2a553b93f301139b2b3c5f787f634e1e109c2d285d82f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b643a385874da4bf6775f582cd51fe7fd53e462c7340d969af43b9c835b981)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsFile",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsFile:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6771747ca7e1f7b5f816c9e39227a9c96726535d79bcec3c5afa25d9fe0dce4)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__186d3bc84c901d510186859f0d6260b903f2f80140fc139e1db36ec32e22b4e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd17c07d32237bacc6ed145052d7683e422bd24352d91838ceba4892ac5f6a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19eb9cb25b762d30e06b23d6982aad1ef9888793ef1d32c1a60479cb5eeff222)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsGcs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsGcs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8119a1c44a9d33e309c789fe4012db8fbf552c9dc8db2f3958ff3d6f7740939)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsGcs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsGcsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsGcsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f142ac7d25678eccc9a142c4d0adce30330708c4fb7e549abaa2ace92f7d38d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e18a83c0ab521c040d58d70296579e447f4755a06bfdd51ce015c69459d138)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cedef98dc63d1d5a2d44d1eab9b885c74e1a30cfbfda138d7dd613c6f2320ed8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoInitScriptsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0896191ec64d6765caa2b8e3b84ae4e3928ddcd86d246ced1e45aa852e76b1c5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksClusterClusterInfoInitScriptsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb866e116272148460e1709a8c4f773d4d2be27bf28f78cd8f0f104e5143b45f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksClusterClusterInfoInitScriptsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9b1ffd84c1011a333e06c61385c6a356125ff9deda17dc87174aac90a808b11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba7de68bc3bfcd803101f29b30ee77e7e5c8a40df06f06f504ca99baf7215b21)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e549cbcfc2730dab1c5a70191067d66936393a6e5a58ca4b6fb5e1c1eeba492d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d38ff722c9fb51e122c8c3098c072c0bb17458c6d0dd81ee6da5257ae04759)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoInitScriptsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da5ad84eb29f7b84f43f234d53bc39c6a83e6157df2a7d7f9d411025001d7f62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAbfss")
    def put_abfss(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsAbfss(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putAbfss", [value]))

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsDbfs(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putFile")
    def put_file(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsFile(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putFile", [value]))

    @jsii.member(jsii_name="putGcs")
    def put_gcs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsGcs(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putGcs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsVolumes(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="putWorkspace")
    def put_workspace(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoInitScriptsWorkspace(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putWorkspace", [value]))

    @jsii.member(jsii_name="resetAbfss")
    def reset_abfss(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbfss", []))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetFile")
    def reset_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFile", []))

    @jsii.member(jsii_name="resetGcs")
    def reset_gcs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @jsii.member(jsii_name="resetWorkspace")
    def reset_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspace", []))

    @builtins.property
    @jsii.member(jsii_name="abfss")
    def abfss(self) -> DataDatabricksClusterClusterInfoInitScriptsAbfssOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoInitScriptsAbfssOutputReference, jsii.get(self, "abfss"))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(self) -> DataDatabricksClusterClusterInfoInitScriptsDbfsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoInitScriptsDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="file")
    def file(self) -> DataDatabricksClusterClusterInfoInitScriptsFileOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoInitScriptsFileOutputReference, jsii.get(self, "file"))

    @builtins.property
    @jsii.member(jsii_name="gcs")
    def gcs(self) -> DataDatabricksClusterClusterInfoInitScriptsGcsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoInitScriptsGcsOutputReference, jsii.get(self, "gcs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(self) -> "DataDatabricksClusterClusterInfoInitScriptsS3OutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoInitScriptsS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(
        self,
    ) -> "DataDatabricksClusterClusterInfoInitScriptsVolumesOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoInitScriptsVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="workspace")
    def workspace(
        self,
    ) -> "DataDatabricksClusterClusterInfoInitScriptsWorkspaceOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoInitScriptsWorkspaceOutputReference", jsii.get(self, "workspace"))

    @builtins.property
    @jsii.member(jsii_name="abfssInput")
    def abfss_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss], jsii.get(self, "abfssInput"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="fileInput")
    def file_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile], jsii.get(self, "fileInput"))

    @builtins.property
    @jsii.member(jsii_name="gcsInput")
    def gcs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs], jsii.get(self, "gcsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsS3"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsVolumes"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceInput")
    def workspace_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoInitScriptsWorkspace"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoInitScriptsWorkspace"], jsii.get(self, "workspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoInitScripts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoInitScripts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoInitScripts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b46104a6bc3a5a0bb0d04c89fe99c3ac21a8b4dfbe0d9d3ee61667c92fcff6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class DataDatabricksClusterClusterInfoInitScriptsS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de6bdda243f03c63317190e2fa6a90f5ecad11a838cea6269d710d0b00cbbf89)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__99a3af6ad7a0874b5c2ba8b9f1ead79f393744d63ec93822f574f48eafc53a49)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b1f77d1d8f129043e42463c6b553be965ab906e6cb4ec3e2622c28f98898920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa340dc44e54714f7044c8864ecd1b714218b029439c0a1b5c8f89d234a3eae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22fef37dbdc0c9a000effe467db1351cff646f9e19578466f246f10dfd82d4b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2f707d92827505404bccbc1220f682877a61ce1eb5d8d360caa463df02246c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9ebc84c825d1cada3a2a484af58612baa9003991320a57735e82d3e7bb168aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__480e912c3f3f1bc40949a7f07f427b9f8fbe1536dcbcb227abdbdf6cae809e97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__360c3b80e269927746a6ce6f5a995a7d451b5d2e2b27effb6a6f5e697a9a5522)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsS3]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2efe4deed92debc3489555cb6d03914a8bc3ea80e3a3d154ad3e2c0acd0d87b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b2a2888be6b8322c0dac27494901cf734b9bac801e0de61459988d789871308)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3a11ec869270e1ee1e91ea5592c26d4b7b0418690af3aa98492825fc64edd48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff6d30880891dbdedd76b28aedca1f14e25a4a806b5d00e35459b8c82ab4584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsVolumes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5463eaeac134db73a89b89ac7a5f5a9af45810e1e7de2fd975b960f9bc04cf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsWorkspace",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoInitScriptsWorkspace:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd52f4c0f71e106d7562a553714e191d168c90273dace00150df66f27ea7f91)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoInitScriptsWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoInitScriptsWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoInitScriptsWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f89bd0ece3554024f9c2e4fc487aff29b253dcc7c55e3df1a28010b485a8cbd6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a5d03358a356128c0b8606c98eaaa1036af545031711de5f030ecb137944c89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoInitScriptsWorkspace]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoInitScriptsWorkspace], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsWorkspace],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e26e6a50ceb29ec2beb9f73a973a1a704818ebb128a4192fced05b41126be68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a5c3229869d17b8538244b0fdd11725325d1a4fda2e92d873648bcfc84af2cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoscale")
    def put_autoscale(
        self,
        *,
        max_workers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.
        '''
        value = DataDatabricksClusterClusterInfoAutoscale(
            max_workers=max_workers, min_workers=min_workers
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscale", [value]))

    @jsii.member(jsii_name="putAwsAttributes")
    def put_aws_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        value = DataDatabricksClusterClusterInfoAwsAttributes(
            availability=availability,
            ebs_volume_count=ebs_volume_count,
            ebs_volume_iops=ebs_volume_iops,
            ebs_volume_size=ebs_volume_size,
            ebs_volume_throughput=ebs_volume_throughput,
            ebs_volume_type=ebs_volume_type,
            first_on_demand=first_on_demand,
            instance_profile_arn=instance_profile_arn,
            spot_bid_price_percent=spot_bid_price_percent,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAwsAttributes", [value]))

    @jsii.member(jsii_name="putAzureAttributes")
    def put_azure_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.
        '''
        value = DataDatabricksClusterClusterInfoAzureAttributes(
            availability=availability,
            first_on_demand=first_on_demand,
            log_analytics_info=log_analytics_info,
            spot_bid_max_price=spot_bid_max_price,
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAttributes", [value]))

    @jsii.member(jsii_name="putClusterLogConf")
    def put_cluster_log_conf(
        self,
        *,
        dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        value = DataDatabricksClusterClusterInfoClusterLogConf(
            dbfs=dbfs, s3=s3, volumes=volumes
        )

        return typing.cast(None, jsii.invoke(self, "putClusterLogConf", [value]))

    @jsii.member(jsii_name="putClusterLogStatus")
    def put_cluster_log_status(
        self,
        *,
        last_attempted: typing.Optional[jsii.Number] = None,
        last_exception: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param last_attempted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_attempted DataDatabricksCluster#last_attempted}.
        :param last_exception: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#last_exception DataDatabricksCluster#last_exception}.
        '''
        value = DataDatabricksClusterClusterInfoClusterLogStatus(
            last_attempted=last_attempted, last_exception=last_exception
        )

        return typing.cast(None, jsii.invoke(self, "putClusterLogStatus", [value]))

    @jsii.member(jsii_name="putDockerImage")
    def put_docker_image(
        self,
        *,
        basic_auth: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.
        '''
        value = DataDatabricksClusterClusterInfoDockerImage(
            basic_auth=basic_auth, url=url
        )

        return typing.cast(None, jsii.invoke(self, "putDockerImage", [value]))

    @jsii.member(jsii_name="putDriver")
    def put_driver(
        self,
        *,
        host_private_ip: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        node_aws_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        node_id: typing.Optional[builtins.str] = None,
        private_ip: typing.Optional[builtins.str] = None,
        public_dns: typing.Optional[builtins.str] = None,
        start_timestamp: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param host_private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#host_private_ip DataDatabricksCluster#host_private_ip}.
        :param instance_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_id DataDatabricksCluster#instance_id}.
        :param node_aws_attributes: node_aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_aws_attributes DataDatabricksCluster#node_aws_attributes}
        :param node_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_id DataDatabricksCluster#node_id}.
        :param private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#private_ip DataDatabricksCluster#private_ip}.
        :param public_dns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#public_dns DataDatabricksCluster#public_dns}.
        :param start_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#start_timestamp DataDatabricksCluster#start_timestamp}.
        '''
        value = DataDatabricksClusterClusterInfoDriver(
            host_private_ip=host_private_ip,
            instance_id=instance_id,
            node_aws_attributes=node_aws_attributes,
            node_id=node_id,
            private_ip=private_ip,
            public_dns=public_dns,
            start_timestamp=start_timestamp,
        )

        return typing.cast(None, jsii.invoke(self, "putDriver", [value]))

    @jsii.member(jsii_name="putExecutors")
    def put_executors(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoExecutors, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea4dba3a385208fb13805fadd1f155550c32ce064bad6368b3552ec8ea414924)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExecutors", [value]))

    @jsii.member(jsii_name="putGcpAttributes")
    def put_gcp_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        boot_disk_size: typing.Optional[jsii.Number] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param boot_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.
        :param use_preemptible_executors: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        value = DataDatabricksClusterClusterInfoGcpAttributes(
            availability=availability,
            boot_disk_size=boot_disk_size,
            first_on_demand=first_on_demand,
            google_service_account=google_service_account,
            local_ssd_count=local_ssd_count,
            use_preemptible_executors=use_preemptible_executors,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpAttributes", [value]))

    @jsii.member(jsii_name="putInitScripts")
    def put_init_scripts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoInitScripts, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb57a0d04bc6f0fe19afe3d5dece9516db82abd4de0cc090395cb4349372bea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInitScripts", [value]))

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        *,
        apply_policy_default_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAutoscale", typing.Dict[builtins.str, typing.Any]]] = None,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_log_conf: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecClusterLogConf", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_mount_info: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecClusterMountInfo", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data_security_mode: typing.Optional[builtins.str] = None,
        docker_image: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecDockerImage", typing.Dict[builtins.str, typing.Any]]] = None,
        driver_instance_pool_id: typing.Optional[builtins.str] = None,
        driver_node_type_id: typing.Optional[builtins.str] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        idempotency_token: typing.Optional[builtins.str] = None,
        init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecInitScripts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        kind: typing.Optional[builtins.str] = None,
        library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecLibrary", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        num_workers: typing.Optional[jsii.Number] = None,
        policy_id: typing.Optional[builtins.str] = None,
        remote_disk_throughput: typing.Optional[jsii.Number] = None,
        runtime_engine: typing.Optional[builtins.str] = None,
        single_user_name: typing.Optional[builtins.str] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_version: typing.Optional[builtins.str] = None,
        ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
        use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_type: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecWorkloadType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param apply_policy_default_values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#apply_policy_default_values DataDatabricksCluster#apply_policy_default_values}.
        :param autoscale: autoscale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        :param cluster_log_conf: cluster_log_conf block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        :param cluster_mount_info: cluster_mount_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_mount_info DataDatabricksCluster#cluster_mount_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.
        :param data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.
        :param docker_image: docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        :param driver_instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.
        :param driver_node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.
        :param enable_local_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        :param idempotency_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#idempotency_token DataDatabricksCluster#idempotency_token}.
        :param init_scripts: init_scripts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.
        :param is_single_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.
        :param library: library block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#library DataDatabricksCluster#library}
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.
        :param num_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.
        :param remote_disk_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.
        :param runtime_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.
        :param single_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.
        :param spark_conf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.
        :param spark_env_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.
        :param spark_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.
        :param ssh_public_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.
        :param total_initial_remote_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.
        :param use_ml_runtime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.
        :param workload_type: workload_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        value = DataDatabricksClusterClusterInfoSpec(
            apply_policy_default_values=apply_policy_default_values,
            autoscale=autoscale,
            aws_attributes=aws_attributes,
            azure_attributes=azure_attributes,
            cluster_log_conf=cluster_log_conf,
            cluster_mount_info=cluster_mount_info,
            cluster_name=cluster_name,
            custom_tags=custom_tags,
            data_security_mode=data_security_mode,
            docker_image=docker_image,
            driver_instance_pool_id=driver_instance_pool_id,
            driver_node_type_id=driver_node_type_id,
            enable_elastic_disk=enable_elastic_disk,
            enable_local_disk_encryption=enable_local_disk_encryption,
            gcp_attributes=gcp_attributes,
            idempotency_token=idempotency_token,
            init_scripts=init_scripts,
            instance_pool_id=instance_pool_id,
            is_single_node=is_single_node,
            kind=kind,
            library=library,
            node_type_id=node_type_id,
            num_workers=num_workers,
            policy_id=policy_id,
            remote_disk_throughput=remote_disk_throughput,
            runtime_engine=runtime_engine,
            single_user_name=single_user_name,
            spark_conf=spark_conf,
            spark_env_vars=spark_env_vars,
            spark_version=spark_version,
            ssh_public_keys=ssh_public_keys,
            total_initial_remote_disk_size=total_initial_remote_disk_size,
            use_ml_runtime=use_ml_runtime,
            workload_type=workload_type,
        )

        return typing.cast(None, jsii.invoke(self, "putSpec", [value]))

    @jsii.member(jsii_name="putTerminationReason")
    def put_termination_reason(
        self,
        *,
        code: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#code DataDatabricksCluster#code}.
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#parameters DataDatabricksCluster#parameters}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#type DataDatabricksCluster#type}.
        '''
        value = DataDatabricksClusterClusterInfoTerminationReason(
            code=code, parameters=parameters, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putTerminationReason", [value]))

    @jsii.member(jsii_name="putWorkloadType")
    def put_workload_type(
        self,
        *,
        clients: typing.Union["DataDatabricksClusterClusterInfoWorkloadTypeClients", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param clients: clients block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        value = DataDatabricksClusterClusterInfoWorkloadType(clients=clients)

        return typing.cast(None, jsii.invoke(self, "putWorkloadType", [value]))

    @jsii.member(jsii_name="resetAutoscale")
    def reset_autoscale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscale", []))

    @jsii.member(jsii_name="resetAutoterminationMinutes")
    def reset_autotermination_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoterminationMinutes", []))

    @jsii.member(jsii_name="resetAwsAttributes")
    def reset_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAttributes", []))

    @jsii.member(jsii_name="resetAzureAttributes")
    def reset_azure_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAttributes", []))

    @jsii.member(jsii_name="resetClusterCores")
    def reset_cluster_cores(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterCores", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetClusterLogConf")
    def reset_cluster_log_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterLogConf", []))

    @jsii.member(jsii_name="resetClusterLogStatus")
    def reset_cluster_log_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterLogStatus", []))

    @jsii.member(jsii_name="resetClusterMemoryMb")
    def reset_cluster_memory_mb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMemoryMb", []))

    @jsii.member(jsii_name="resetClusterName")
    def reset_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterName", []))

    @jsii.member(jsii_name="resetClusterSource")
    def reset_cluster_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterSource", []))

    @jsii.member(jsii_name="resetCreatorUserName")
    def reset_creator_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatorUserName", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDataSecurityMode")
    def reset_data_security_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSecurityMode", []))

    @jsii.member(jsii_name="resetDefaultTags")
    def reset_default_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTags", []))

    @jsii.member(jsii_name="resetDockerImage")
    def reset_docker_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerImage", []))

    @jsii.member(jsii_name="resetDriver")
    def reset_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriver", []))

    @jsii.member(jsii_name="resetDriverInstancePoolId")
    def reset_driver_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverInstancePoolId", []))

    @jsii.member(jsii_name="resetDriverNodeTypeId")
    def reset_driver_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverNodeTypeId", []))

    @jsii.member(jsii_name="resetEnableElasticDisk")
    def reset_enable_elastic_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableElasticDisk", []))

    @jsii.member(jsii_name="resetEnableLocalDiskEncryption")
    def reset_enable_local_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLocalDiskEncryption", []))

    @jsii.member(jsii_name="resetExecutors")
    def reset_executors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutors", []))

    @jsii.member(jsii_name="resetGcpAttributes")
    def reset_gcp_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAttributes", []))

    @jsii.member(jsii_name="resetInitScripts")
    def reset_init_scripts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitScripts", []))

    @jsii.member(jsii_name="resetInstancePoolId")
    def reset_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolId", []))

    @jsii.member(jsii_name="resetIsSingleNode")
    def reset_is_single_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSingleNode", []))

    @jsii.member(jsii_name="resetJdbcPort")
    def reset_jdbc_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJdbcPort", []))

    @jsii.member(jsii_name="resetKind")
    def reset_kind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKind", []))

    @jsii.member(jsii_name="resetLastRestartedTime")
    def reset_last_restarted_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastRestartedTime", []))

    @jsii.member(jsii_name="resetLastStateLossTime")
    def reset_last_state_loss_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastStateLossTime", []))

    @jsii.member(jsii_name="resetNodeTypeId")
    def reset_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeTypeId", []))

    @jsii.member(jsii_name="resetNumWorkers")
    def reset_num_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumWorkers", []))

    @jsii.member(jsii_name="resetPolicyId")
    def reset_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyId", []))

    @jsii.member(jsii_name="resetRemoteDiskThroughput")
    def reset_remote_disk_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteDiskThroughput", []))

    @jsii.member(jsii_name="resetRuntimeEngine")
    def reset_runtime_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuntimeEngine", []))

    @jsii.member(jsii_name="resetSingleUserName")
    def reset_single_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSingleUserName", []))

    @jsii.member(jsii_name="resetSparkConf")
    def reset_spark_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkConf", []))

    @jsii.member(jsii_name="resetSparkContextId")
    def reset_spark_context_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkContextId", []))

    @jsii.member(jsii_name="resetSparkEnvVars")
    def reset_spark_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkEnvVars", []))

    @jsii.member(jsii_name="resetSparkVersion")
    def reset_spark_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkVersion", []))

    @jsii.member(jsii_name="resetSpec")
    def reset_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpec", []))

    @jsii.member(jsii_name="resetSshPublicKeys")
    def reset_ssh_public_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshPublicKeys", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetStateMessage")
    def reset_state_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStateMessage", []))

    @jsii.member(jsii_name="resetTerminatedTime")
    def reset_terminated_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminatedTime", []))

    @jsii.member(jsii_name="resetTerminationReason")
    def reset_termination_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationReason", []))

    @jsii.member(jsii_name="resetTotalInitialRemoteDiskSize")
    def reset_total_initial_remote_disk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalInitialRemoteDiskSize", []))

    @jsii.member(jsii_name="resetUseMlRuntime")
    def reset_use_ml_runtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseMlRuntime", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="autoscale")
    def autoscale(self) -> DataDatabricksClusterClusterInfoAutoscaleOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoAutoscaleOutputReference, jsii.get(self, "autoscale"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributes")
    def aws_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoAwsAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoAwsAttributesOutputReference, jsii.get(self, "awsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributes")
    def azure_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoAzureAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoAzureAttributesOutputReference, jsii.get(self, "azureAttributes"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConf")
    def cluster_log_conf(
        self,
    ) -> DataDatabricksClusterClusterInfoClusterLogConfOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoClusterLogConfOutputReference, jsii.get(self, "clusterLogConf"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogStatus")
    def cluster_log_status(
        self,
    ) -> DataDatabricksClusterClusterInfoClusterLogStatusOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoClusterLogStatusOutputReference, jsii.get(self, "clusterLogStatus"))

    @builtins.property
    @jsii.member(jsii_name="dockerImage")
    def docker_image(
        self,
    ) -> DataDatabricksClusterClusterInfoDockerImageOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoDockerImageOutputReference, jsii.get(self, "dockerImage"))

    @builtins.property
    @jsii.member(jsii_name="driver")
    def driver(self) -> DataDatabricksClusterClusterInfoDriverOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoDriverOutputReference, jsii.get(self, "driver"))

    @builtins.property
    @jsii.member(jsii_name="executors")
    def executors(self) -> DataDatabricksClusterClusterInfoExecutorsList:
        return typing.cast(DataDatabricksClusterClusterInfoExecutorsList, jsii.get(self, "executors"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributes")
    def gcp_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoGcpAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoGcpAttributesOutputReference, jsii.get(self, "gcpAttributes"))

    @builtins.property
    @jsii.member(jsii_name="initScripts")
    def init_scripts(self) -> DataDatabricksClusterClusterInfoInitScriptsList:
        return typing.cast(DataDatabricksClusterClusterInfoInitScriptsList, jsii.get(self, "initScripts"))

    @builtins.property
    @jsii.member(jsii_name="spec")
    def spec(self) -> "DataDatabricksClusterClusterInfoSpecOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecOutputReference", jsii.get(self, "spec"))

    @builtins.property
    @jsii.member(jsii_name="terminationReason")
    def termination_reason(
        self,
    ) -> "DataDatabricksClusterClusterInfoTerminationReasonOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoTerminationReasonOutputReference", jsii.get(self, "terminationReason"))

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(
        self,
    ) -> "DataDatabricksClusterClusterInfoWorkloadTypeOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoWorkloadTypeOutputReference", jsii.get(self, "workloadType"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleInput")
    def autoscale_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAutoscale]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAutoscale], jsii.get(self, "autoscaleInput"))

    @builtins.property
    @jsii.member(jsii_name="autoterminationMinutesInput")
    def autotermination_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoterminationMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributesInput")
    def aws_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes], jsii.get(self, "awsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributesInput")
    def azure_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes], jsii.get(self, "azureAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterCoresInput")
    def cluster_cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterCoresInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConfInput")
    def cluster_log_conf_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf], jsii.get(self, "clusterLogConfInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogStatusInput")
    def cluster_log_status_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus], jsii.get(self, "clusterLogStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterMemoryMbInput")
    def cluster_memory_mb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterMemoryMbInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterSourceInput")
    def cluster_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorUserNameInput")
    def creator_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creatorUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSecurityModeInput")
    def data_security_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTagsInput")
    def default_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "defaultTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="dockerImageInput")
    def docker_image_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoDockerImage]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDockerImage], jsii.get(self, "dockerImageInput"))

    @builtins.property
    @jsii.member(jsii_name="driverInput")
    def driver_input(self) -> typing.Optional[DataDatabricksClusterClusterInfoDriver]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoDriver], jsii.get(self, "driverInput"))

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolIdInput")
    def driver_instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInstancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeIdInput")
    def driver_node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverNodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enableElasticDiskInput")
    def enable_elastic_disk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableElasticDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryptionInput")
    def enable_local_disk_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableLocalDiskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="executorsInput")
    def executors_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]], jsii.get(self, "executorsInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributesInput")
    def gcp_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes], jsii.get(self, "gcpAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="initScriptsInput")
    def init_scripts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]], jsii.get(self, "initScriptsInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolIdInput")
    def instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="isSingleNodeInput")
    def is_single_node_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSingleNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="jdbcPortInput")
    def jdbc_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jdbcPortInput"))

    @builtins.property
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property
    @jsii.member(jsii_name="lastRestartedTimeInput")
    def last_restarted_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastRestartedTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="lastStateLossTimeInput")
    def last_state_loss_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastStateLossTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeIdInput")
    def node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="numWorkersInput")
    def num_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteDiskThroughputInput")
    def remote_disk_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "remoteDiskThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="runtimeEngineInput")
    def runtime_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeEngineInput"))

    @builtins.property
    @jsii.member(jsii_name="singleUserNameInput")
    def single_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "singleUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkConfInput")
    def spark_conf_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkConfInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkContextIdInput")
    def spark_context_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sparkContextIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVarsInput")
    def spark_env_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkEnvVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkVersionInput")
    def spark_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sparkVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="specInput")
    def spec_input(self) -> typing.Optional["DataDatabricksClusterClusterInfoSpec"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpec"], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeysInput")
    def ssh_public_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshPublicKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="stateMessageInput")
    def state_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="terminatedTimeInput")
    def terminated_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "terminatedTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationReasonInput")
    def termination_reason_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoTerminationReason"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoTerminationReason"], jsii.get(self, "terminationReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="totalInitialRemoteDiskSizeInput")
    def total_initial_remote_disk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalInitialRemoteDiskSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="useMlRuntimeInput")
    def use_ml_runtime_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useMlRuntimeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoWorkloadType"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoWorkloadType"], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="autoterminationMinutes")
    def autotermination_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoterminationMinutes"))

    @autotermination_minutes.setter
    def autotermination_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22121b91bd4014ea1c111063accbe2fcff7b706536a17408326c22c59ece23f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoterminationMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterCores")
    def cluster_cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterCores"))

    @cluster_cores.setter
    def cluster_cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03db98a9820b5b21f508013c38284758670d05dea19de653e35c86a6af9b8871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterCores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15d6e1915ec10f28cf0442ccb18bdc25429b5cbfe36a6d916168de159209ea06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterMemoryMb")
    def cluster_memory_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterMemoryMb"))

    @cluster_memory_mb.setter
    def cluster_memory_mb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f86145d9f6a8b67abe506e589523463bf2f6ab39326a24a5218fb7ed6011ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterMemoryMb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06a9b58ff1c6bbf8bfcb6987139edf512379e2fe382bca0d6e54086eaaec9f97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterSource")
    def cluster_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterSource"))

    @cluster_source.setter
    def cluster_source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68cb61f4e419bd8ada9dd7fd086ad784b217bc959cddc3b85f631f69a433f055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterSource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creatorUserName")
    def creator_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creatorUserName"))

    @creator_user_name.setter
    def creator_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31b37e9eccc44dab6d644af18d605f326841bd3bbd84fc7077a3dc46622bffe0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creatorUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7fc76b37a2344f7dc3fa1e30ff8dd6c0b355f384fd6a03f706fd0a98fb18133)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSecurityMode")
    def data_security_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSecurityMode"))

    @data_security_mode.setter
    def data_security_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41366137ff035417d9e13cf6cead0550b62e987e06afaded60d1a2e6b3dfab62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSecurityMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTags")
    def default_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "defaultTags"))

    @default_tags.setter
    def default_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def4a2e6601323908a266d721257bc0b5df9a86d95e565037241c75745b6fe55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolId")
    def driver_instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverInstancePoolId"))

    @driver_instance_pool_id.setter
    def driver_instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f09485e0c6efdcef7ee9203ea9184b140b7edb5c0f7c9c8d78104541288dfac0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverInstancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeId")
    def driver_node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverNodeTypeId"))

    @driver_node_type_id.setter
    def driver_node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246b214c1e0a6af3c91c9ba3b94a919eca345fa37d30bde494cc884bb87eab37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverNodeTypeId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__ecd10f2c0131bee7282573acd48ccd0008fb0ecfa286b5691aa3243a54927b4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableElasticDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryption")
    def enable_local_disk_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableLocalDiskEncryption"))

    @enable_local_disk_encryption.setter
    def enable_local_disk_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57df41759dad7726fd9beb5995fff437d3e29ad8dc71545e8068ffcec8fae100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableLocalDiskEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a21d03f96cf9c1a9413b4e0b13f175f44f0a82e16538ddc701b19f2d0e11c72c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSingleNode")
    def is_single_node(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSingleNode"))

    @is_single_node.setter
    def is_single_node(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d06ed51d59eae974c3ceef641c326c92888c62b8f2ef74d779426edb86b7f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSingleNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jdbcPort")
    def jdbc_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jdbcPort"))

    @jdbc_port.setter
    def jdbc_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72da05a9b56b01f50c0654805697f6c04ce188b2eb712db1948cc917a5069d3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jdbcPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efbfa61a14c03be599ca26436983701cf9f4d325ba7b90665909f1fbe316648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastRestartedTime")
    def last_restarted_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastRestartedTime"))

    @last_restarted_time.setter
    def last_restarted_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46f4dded366a647ec88392a5c521dbe7aa46383a34a1d8e75e209b695b78744)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastRestartedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastStateLossTime")
    def last_state_loss_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastStateLossTime"))

    @last_state_loss_time.setter
    def last_state_loss_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e57b69bfb7f4c1832fca3fecee3b59b954cd85300b5bc7b99a673aa51ec93e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastStateLossTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50b090777c2e59f174c04c46025064f4362ff18253fc25a76a2df90aed6413b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numWorkers")
    def num_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numWorkers"))

    @num_workers.setter
    def num_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6aec61206fc698207291fca4b4b5fe4b42a5777d37e780be5873e22d249abcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8e484c951fd458cca10605cd89905bc4548e9a51b8d702bae02d89373de09c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteDiskThroughput")
    def remote_disk_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "remoteDiskThroughput"))

    @remote_disk_throughput.setter
    def remote_disk_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c02815a4129b7caa3178d6324d016315f6edeb7a7b25276f331f6d40709b10c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteDiskThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runtimeEngine")
    def runtime_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtimeEngine"))

    @runtime_engine.setter
    def runtime_engine(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fa92c977350a6bef48287ce2a6666b27c9c9a5eacc361eca7934b5b7f678fc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runtimeEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="singleUserName")
    def single_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "singleUserName"))

    @single_user_name.setter
    def single_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2215a4c7634eb1444c55048d14b27a51cddfabf211182b054794c0473cd8bb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "singleUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkConf")
    def spark_conf(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkConf"))

    @spark_conf.setter
    def spark_conf(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb50e299d9342c6694edd25abec64c6e72a3a3cb4e34491fce28994c5a88d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkConf", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkContextId")
    def spark_context_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sparkContextId"))

    @spark_context_id.setter
    def spark_context_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8473f32c0d37a0a58e04928313fb1e21b4b4dda8fc6cdd8a30beb1f5761ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkContextId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVars")
    def spark_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkEnvVars"))

    @spark_env_vars.setter
    def spark_env_vars(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e09b37cd8f3c047187ca1a05924812e0553aec526ed5110a2fe486ce117b1191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkEnvVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkVersion")
    def spark_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sparkVersion"))

    @spark_version.setter
    def spark_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8c520ec003f8cca5a1439b11e26c25036c47b356b34363f2080f673d80902df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeys")
    def ssh_public_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshPublicKeys"))

    @ssh_public_keys.setter
    def ssh_public_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__809e7b8f4cbe076dec36d64d6d802d0291a14b875f81847cd7571ee69d2cc2be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshPublicKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9684945163bfda726d2dd47510681d1789c0d4a3bd95271fb7d776a641064852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fffa21e7caf53e99645e13e4ea1cfd6d41765d5b6a5bea56d5d112b1462d0fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stateMessage")
    def state_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateMessage"))

    @state_message.setter
    def state_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd7eaebf00b101618eecb0adb8535fcb14575c7aa315b3385ada64de8ea4d35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminatedTime")
    def terminated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "terminatedTime"))

    @terminated_time.setter
    def terminated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d91e761ee85cd3837f32f6ea64eaabcbf3a984db59c7cb25790c38cbf5c7a96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminatedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalInitialRemoteDiskSize")
    def total_initial_remote_disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalInitialRemoteDiskSize"))

    @total_initial_remote_disk_size.setter
    def total_initial_remote_disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__752b90076eba86da3309f0b8a03d34859f847c197645e0964a8e563e81537d12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalInitialRemoteDiskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useMlRuntime")
    def use_ml_runtime(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useMlRuntime"))

    @use_ml_runtime.setter
    def use_ml_runtime(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f10ac7dea6b3ceaff0344a26cd17eb415162f54630339912ce949cc5e2746ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useMlRuntime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksClusterClusterInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd3ff2999b11adebf3904d46bd1e1f111e4ce29eeb41862c0eff3638cc021870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpec",
    jsii_struct_bases=[],
    name_mapping={
        "apply_policy_default_values": "applyPolicyDefaultValues",
        "autoscale": "autoscale",
        "aws_attributes": "awsAttributes",
        "azure_attributes": "azureAttributes",
        "cluster_log_conf": "clusterLogConf",
        "cluster_mount_info": "clusterMountInfo",
        "cluster_name": "clusterName",
        "custom_tags": "customTags",
        "data_security_mode": "dataSecurityMode",
        "docker_image": "dockerImage",
        "driver_instance_pool_id": "driverInstancePoolId",
        "driver_node_type_id": "driverNodeTypeId",
        "enable_elastic_disk": "enableElasticDisk",
        "enable_local_disk_encryption": "enableLocalDiskEncryption",
        "gcp_attributes": "gcpAttributes",
        "idempotency_token": "idempotencyToken",
        "init_scripts": "initScripts",
        "instance_pool_id": "instancePoolId",
        "is_single_node": "isSingleNode",
        "kind": "kind",
        "library": "library",
        "node_type_id": "nodeTypeId",
        "num_workers": "numWorkers",
        "policy_id": "policyId",
        "remote_disk_throughput": "remoteDiskThroughput",
        "runtime_engine": "runtimeEngine",
        "single_user_name": "singleUserName",
        "spark_conf": "sparkConf",
        "spark_env_vars": "sparkEnvVars",
        "spark_version": "sparkVersion",
        "ssh_public_keys": "sshPublicKeys",
        "total_initial_remote_disk_size": "totalInitialRemoteDiskSize",
        "use_ml_runtime": "useMlRuntime",
        "workload_type": "workloadType",
    },
)
class DataDatabricksClusterClusterInfoSpec:
    def __init__(
        self,
        *,
        apply_policy_default_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAutoscale", typing.Dict[builtins.str, typing.Any]]] = None,
        aws_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_log_conf: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecClusterLogConf", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_mount_info: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecClusterMountInfo", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data_security_mode: typing.Optional[builtins.str] = None,
        docker_image: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecDockerImage", typing.Dict[builtins.str, typing.Any]]] = None,
        driver_instance_pool_id: typing.Optional[builtins.str] = None,
        driver_node_type_id: typing.Optional[builtins.str] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        idempotency_token: typing.Optional[builtins.str] = None,
        init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecInitScripts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        kind: typing.Optional[builtins.str] = None,
        library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksClusterClusterInfoSpecLibrary", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        num_workers: typing.Optional[jsii.Number] = None,
        policy_id: typing.Optional[builtins.str] = None,
        remote_disk_throughput: typing.Optional[jsii.Number] = None,
        runtime_engine: typing.Optional[builtins.str] = None,
        single_user_name: typing.Optional[builtins.str] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_version: typing.Optional[builtins.str] = None,
        ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
        use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        workload_type: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecWorkloadType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param apply_policy_default_values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#apply_policy_default_values DataDatabricksCluster#apply_policy_default_values}.
        :param autoscale: autoscale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        :param cluster_log_conf: cluster_log_conf block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        :param cluster_mount_info: cluster_mount_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_mount_info DataDatabricksCluster#cluster_mount_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.
        :param data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.
        :param docker_image: docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        :param driver_instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.
        :param driver_node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.
        :param enable_local_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        :param idempotency_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#idempotency_token DataDatabricksCluster#idempotency_token}.
        :param init_scripts: init_scripts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.
        :param is_single_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.
        :param library: library block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#library DataDatabricksCluster#library}
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.
        :param num_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.
        :param remote_disk_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.
        :param runtime_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.
        :param single_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.
        :param spark_conf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.
        :param spark_env_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.
        :param spark_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.
        :param ssh_public_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.
        :param total_initial_remote_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.
        :param use_ml_runtime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.
        :param workload_type: workload_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        if isinstance(autoscale, dict):
            autoscale = DataDatabricksClusterClusterInfoSpecAutoscale(**autoscale)
        if isinstance(aws_attributes, dict):
            aws_attributes = DataDatabricksClusterClusterInfoSpecAwsAttributes(**aws_attributes)
        if isinstance(azure_attributes, dict):
            azure_attributes = DataDatabricksClusterClusterInfoSpecAzureAttributes(**azure_attributes)
        if isinstance(cluster_log_conf, dict):
            cluster_log_conf = DataDatabricksClusterClusterInfoSpecClusterLogConf(**cluster_log_conf)
        if isinstance(docker_image, dict):
            docker_image = DataDatabricksClusterClusterInfoSpecDockerImage(**docker_image)
        if isinstance(gcp_attributes, dict):
            gcp_attributes = DataDatabricksClusterClusterInfoSpecGcpAttributes(**gcp_attributes)
        if isinstance(workload_type, dict):
            workload_type = DataDatabricksClusterClusterInfoSpecWorkloadType(**workload_type)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b3d6502e1c7cc70d1c52b28d46cfa1bc967892f5044f8f4f56035e6b6a7ac6)
            check_type(argname="argument apply_policy_default_values", value=apply_policy_default_values, expected_type=type_hints["apply_policy_default_values"])
            check_type(argname="argument autoscale", value=autoscale, expected_type=type_hints["autoscale"])
            check_type(argname="argument aws_attributes", value=aws_attributes, expected_type=type_hints["aws_attributes"])
            check_type(argname="argument azure_attributes", value=azure_attributes, expected_type=type_hints["azure_attributes"])
            check_type(argname="argument cluster_log_conf", value=cluster_log_conf, expected_type=type_hints["cluster_log_conf"])
            check_type(argname="argument cluster_mount_info", value=cluster_mount_info, expected_type=type_hints["cluster_mount_info"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument data_security_mode", value=data_security_mode, expected_type=type_hints["data_security_mode"])
            check_type(argname="argument docker_image", value=docker_image, expected_type=type_hints["docker_image"])
            check_type(argname="argument driver_instance_pool_id", value=driver_instance_pool_id, expected_type=type_hints["driver_instance_pool_id"])
            check_type(argname="argument driver_node_type_id", value=driver_node_type_id, expected_type=type_hints["driver_node_type_id"])
            check_type(argname="argument enable_elastic_disk", value=enable_elastic_disk, expected_type=type_hints["enable_elastic_disk"])
            check_type(argname="argument enable_local_disk_encryption", value=enable_local_disk_encryption, expected_type=type_hints["enable_local_disk_encryption"])
            check_type(argname="argument gcp_attributes", value=gcp_attributes, expected_type=type_hints["gcp_attributes"])
            check_type(argname="argument idempotency_token", value=idempotency_token, expected_type=type_hints["idempotency_token"])
            check_type(argname="argument init_scripts", value=init_scripts, expected_type=type_hints["init_scripts"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument is_single_node", value=is_single_node, expected_type=type_hints["is_single_node"])
            check_type(argname="argument kind", value=kind, expected_type=type_hints["kind"])
            check_type(argname="argument library", value=library, expected_type=type_hints["library"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument num_workers", value=num_workers, expected_type=type_hints["num_workers"])
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
            check_type(argname="argument remote_disk_throughput", value=remote_disk_throughput, expected_type=type_hints["remote_disk_throughput"])
            check_type(argname="argument runtime_engine", value=runtime_engine, expected_type=type_hints["runtime_engine"])
            check_type(argname="argument single_user_name", value=single_user_name, expected_type=type_hints["single_user_name"])
            check_type(argname="argument spark_conf", value=spark_conf, expected_type=type_hints["spark_conf"])
            check_type(argname="argument spark_env_vars", value=spark_env_vars, expected_type=type_hints["spark_env_vars"])
            check_type(argname="argument spark_version", value=spark_version, expected_type=type_hints["spark_version"])
            check_type(argname="argument ssh_public_keys", value=ssh_public_keys, expected_type=type_hints["ssh_public_keys"])
            check_type(argname="argument total_initial_remote_disk_size", value=total_initial_remote_disk_size, expected_type=type_hints["total_initial_remote_disk_size"])
            check_type(argname="argument use_ml_runtime", value=use_ml_runtime, expected_type=type_hints["use_ml_runtime"])
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if apply_policy_default_values is not None:
            self._values["apply_policy_default_values"] = apply_policy_default_values
        if autoscale is not None:
            self._values["autoscale"] = autoscale
        if aws_attributes is not None:
            self._values["aws_attributes"] = aws_attributes
        if azure_attributes is not None:
            self._values["azure_attributes"] = azure_attributes
        if cluster_log_conf is not None:
            self._values["cluster_log_conf"] = cluster_log_conf
        if cluster_mount_info is not None:
            self._values["cluster_mount_info"] = cluster_mount_info
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if data_security_mode is not None:
            self._values["data_security_mode"] = data_security_mode
        if docker_image is not None:
            self._values["docker_image"] = docker_image
        if driver_instance_pool_id is not None:
            self._values["driver_instance_pool_id"] = driver_instance_pool_id
        if driver_node_type_id is not None:
            self._values["driver_node_type_id"] = driver_node_type_id
        if enable_elastic_disk is not None:
            self._values["enable_elastic_disk"] = enable_elastic_disk
        if enable_local_disk_encryption is not None:
            self._values["enable_local_disk_encryption"] = enable_local_disk_encryption
        if gcp_attributes is not None:
            self._values["gcp_attributes"] = gcp_attributes
        if idempotency_token is not None:
            self._values["idempotency_token"] = idempotency_token
        if init_scripts is not None:
            self._values["init_scripts"] = init_scripts
        if instance_pool_id is not None:
            self._values["instance_pool_id"] = instance_pool_id
        if is_single_node is not None:
            self._values["is_single_node"] = is_single_node
        if kind is not None:
            self._values["kind"] = kind
        if library is not None:
            self._values["library"] = library
        if node_type_id is not None:
            self._values["node_type_id"] = node_type_id
        if num_workers is not None:
            self._values["num_workers"] = num_workers
        if policy_id is not None:
            self._values["policy_id"] = policy_id
        if remote_disk_throughput is not None:
            self._values["remote_disk_throughput"] = remote_disk_throughput
        if runtime_engine is not None:
            self._values["runtime_engine"] = runtime_engine
        if single_user_name is not None:
            self._values["single_user_name"] = single_user_name
        if spark_conf is not None:
            self._values["spark_conf"] = spark_conf
        if spark_env_vars is not None:
            self._values["spark_env_vars"] = spark_env_vars
        if spark_version is not None:
            self._values["spark_version"] = spark_version
        if ssh_public_keys is not None:
            self._values["ssh_public_keys"] = ssh_public_keys
        if total_initial_remote_disk_size is not None:
            self._values["total_initial_remote_disk_size"] = total_initial_remote_disk_size
        if use_ml_runtime is not None:
            self._values["use_ml_runtime"] = use_ml_runtime
        if workload_type is not None:
            self._values["workload_type"] = workload_type

    @builtins.property
    def apply_policy_default_values(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#apply_policy_default_values DataDatabricksCluster#apply_policy_default_values}.'''
        result = self._values.get("apply_policy_default_values")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autoscale(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecAutoscale"]:
        '''autoscale block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#autoscale DataDatabricksCluster#autoscale}
        '''
        result = self._values.get("autoscale")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecAutoscale"], result)

    @builtins.property
    def aws_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecAwsAttributes"]:
        '''aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#aws_attributes DataDatabricksCluster#aws_attributes}
        '''
        result = self._values.get("aws_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecAwsAttributes"], result)

    @builtins.property
    def azure_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecAzureAttributes"]:
        '''azure_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#azure_attributes DataDatabricksCluster#azure_attributes}
        '''
        result = self._values.get("azure_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecAzureAttributes"], result)

    @builtins.property
    def cluster_log_conf(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConf"]:
        '''cluster_log_conf block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_log_conf DataDatabricksCluster#cluster_log_conf}
        '''
        result = self._values.get("cluster_log_conf")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConf"], result)

    @builtins.property
    def cluster_mount_info(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecClusterMountInfo"]]]:
        '''cluster_mount_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_mount_info DataDatabricksCluster#cluster_mount_info}
        '''
        result = self._values.get("cluster_mount_info")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecClusterMountInfo"]]], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#custom_tags DataDatabricksCluster#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def data_security_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#data_security_mode DataDatabricksCluster#data_security_mode}.'''
        result = self._values.get("data_security_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_image(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecDockerImage"]:
        '''docker_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#docker_image DataDatabricksCluster#docker_image}
        '''
        result = self._values.get("docker_image")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecDockerImage"], result)

    @builtins.property
    def driver_instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_instance_pool_id DataDatabricksCluster#driver_instance_pool_id}.'''
        result = self._values.get("driver_instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#driver_node_type_id DataDatabricksCluster#driver_node_type_id}.'''
        result = self._values.get("driver_node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_elastic_disk(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_elastic_disk DataDatabricksCluster#enable_elastic_disk}.'''
        result = self._values.get("enable_elastic_disk")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_local_disk_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_local_disk_encryption DataDatabricksCluster#enable_local_disk_encryption}.'''
        result = self._values.get("enable_local_disk_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gcp_attributes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecGcpAttributes"]:
        '''gcp_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcp_attributes DataDatabricksCluster#gcp_attributes}
        '''
        result = self._values.get("gcp_attributes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecGcpAttributes"], result)

    @builtins.property
    def idempotency_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#idempotency_token DataDatabricksCluster#idempotency_token}.'''
        result = self._values.get("idempotency_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def init_scripts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecInitScripts"]]]:
        '''init_scripts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#init_scripts DataDatabricksCluster#init_scripts}
        '''
        result = self._values.get("init_scripts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecInitScripts"]]], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_pool_id DataDatabricksCluster#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_single_node(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#is_single_node DataDatabricksCluster#is_single_node}.'''
        result = self._values.get("is_single_node")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def kind(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kind DataDatabricksCluster#kind}.'''
        result = self._values.get("kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def library(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecLibrary"]]]:
        '''library block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#library DataDatabricksCluster#library}
        '''
        result = self._values.get("library")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksClusterClusterInfoSpecLibrary"]]], result)

    @builtins.property
    def node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#node_type_id DataDatabricksCluster#node_type_id}.'''
        result = self._values.get("node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#num_workers DataDatabricksCluster#num_workers}.'''
        result = self._values.get("num_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#policy_id DataDatabricksCluster#policy_id}.'''
        result = self._values.get("policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_disk_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_disk_throughput DataDatabricksCluster#remote_disk_throughput}.'''
        result = self._values.get("remote_disk_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def runtime_engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#runtime_engine DataDatabricksCluster#runtime_engine}.'''
        result = self._values.get("runtime_engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def single_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#single_user_name DataDatabricksCluster#single_user_name}.'''
        result = self._values.get("single_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_conf(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_conf DataDatabricksCluster#spark_conf}.'''
        result = self._values.get("spark_conf")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def spark_env_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_env_vars DataDatabricksCluster#spark_env_vars}.'''
        result = self._values.get("spark_env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def spark_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spark_version DataDatabricksCluster#spark_version}.'''
        result = self._values.get("spark_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_public_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ssh_public_keys DataDatabricksCluster#ssh_public_keys}.'''
        result = self._values.get("ssh_public_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def total_initial_remote_disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#total_initial_remote_disk_size DataDatabricksCluster#total_initial_remote_disk_size}.'''
        result = self._values.get("total_initial_remote_disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def use_ml_runtime(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_ml_runtime DataDatabricksCluster#use_ml_runtime}.'''
        result = self._values.get("use_ml_runtime")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def workload_type(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecWorkloadType"]:
        '''workload_type block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workload_type DataDatabricksCluster#workload_type}
        '''
        result = self._values.get("workload_type")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecWorkloadType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAutoscale",
    jsii_struct_bases=[],
    name_mapping={"max_workers": "maxWorkers", "min_workers": "minWorkers"},
)
class DataDatabricksClusterClusterInfoSpecAutoscale:
    def __init__(
        self,
        *,
        max_workers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cc8bb4fa18897c108e2775c2a93ce1b5278928bd022a47bc49950e5f985af4)
            check_type(argname="argument max_workers", value=max_workers, expected_type=type_hints["max_workers"])
            check_type(argname="argument min_workers", value=min_workers, expected_type=type_hints["min_workers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_workers is not None:
            self._values["max_workers"] = max_workers
        if min_workers is not None:
            self._values["min_workers"] = min_workers

    @builtins.property
    def max_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.'''
        result = self._values.get("max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.'''
        result = self._values.get("min_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecAutoscale(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecAutoscaleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAutoscaleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__595c205794605714edea3ab45ef074d3cadf2d7f23b1fd69e2c4f2c093a72df6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxWorkers")
    def reset_max_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWorkers", []))

    @jsii.member(jsii_name="resetMinWorkers")
    def reset_min_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinWorkers", []))

    @builtins.property
    @jsii.member(jsii_name="maxWorkersInput")
    def max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="minWorkersInput")
    def min_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkers")
    def max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkers"))

    @max_workers.setter
    def max_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d9f16aa330d682bebab179ef6ea77f39fc99393f7153e43c2c11a2274e39c47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minWorkers")
    def min_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minWorkers"))

    @min_workers.setter
    def min_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e4dd149140f7a7ba62be16d5eff46aa0e9aa8a49a97c66c1a79cdd3e91460c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97794810df78630eb0da3fcda55e5d324af7f76e3985395304cacd17ec9d6a24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "ebs_volume_count": "ebsVolumeCount",
        "ebs_volume_iops": "ebsVolumeIops",
        "ebs_volume_size": "ebsVolumeSize",
        "ebs_volume_throughput": "ebsVolumeThroughput",
        "ebs_volume_type": "ebsVolumeType",
        "first_on_demand": "firstOnDemand",
        "instance_profile_arn": "instanceProfileArn",
        "spot_bid_price_percent": "spotBidPricePercent",
        "zone_id": "zoneId",
    },
)
class DataDatabricksClusterClusterInfoSpecAwsAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ecae928782ae3f047a55cb1880eccce780bc0636694759bbf2089f19d6a547c)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument ebs_volume_count", value=ebs_volume_count, expected_type=type_hints["ebs_volume_count"])
            check_type(argname="argument ebs_volume_iops", value=ebs_volume_iops, expected_type=type_hints["ebs_volume_iops"])
            check_type(argname="argument ebs_volume_size", value=ebs_volume_size, expected_type=type_hints["ebs_volume_size"])
            check_type(argname="argument ebs_volume_throughput", value=ebs_volume_throughput, expected_type=type_hints["ebs_volume_throughput"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument spot_bid_price_percent", value=spot_bid_price_percent, expected_type=type_hints["spot_bid_price_percent"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if ebs_volume_count is not None:
            self._values["ebs_volume_count"] = ebs_volume_count
        if ebs_volume_iops is not None:
            self._values["ebs_volume_iops"] = ebs_volume_iops
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if ebs_volume_throughput is not None:
            self._values["ebs_volume_throughput"] = ebs_volume_throughput
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if spot_bid_price_percent is not None:
            self._values["spot_bid_price_percent"] = spot_bid_price_percent
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.'''
        result = self._values.get("ebs_volume_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.'''
        result = self._values.get("ebs_volume_iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.'''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.'''
        result = self._values.get("ebs_volume_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.'''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_price_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.'''
        result = self._values.get("spot_bid_price_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47c80a7bc6c5f8491a32f9c5356e1109069e31af3a66680677c17eb053906675)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetEbsVolumeCount")
    def reset_ebs_volume_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeCount", []))

    @jsii.member(jsii_name="resetEbsVolumeIops")
    def reset_ebs_volume_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeIops", []))

    @jsii.member(jsii_name="resetEbsVolumeSize")
    def reset_ebs_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeSize", []))

    @jsii.member(jsii_name="resetEbsVolumeThroughput")
    def reset_ebs_volume_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeThroughput", []))

    @jsii.member(jsii_name="resetEbsVolumeType")
    def reset_ebs_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeType", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

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
    @jsii.member(jsii_name="ebsVolumeCountInput")
    def ebs_volume_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIopsInput")
    def ebs_volume_iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeIopsInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSizeInput")
    def ebs_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughputInput")
    def ebs_volume_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeTypeInput")
    def ebs_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ebsVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b81cc8b98150b78ff5fc232c180a8b923a1471c7dc7f4caf16d9deb7cd3ee777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeCount")
    def ebs_volume_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeCount"))

    @ebs_volume_count.setter
    def ebs_volume_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bbc3709021f4fed3e3fb2cb1e4b7e1909c88ff243555840282dab10f58e8d7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIops")
    def ebs_volume_iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeIops"))

    @ebs_volume_iops.setter
    def ebs_volume_iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba8c27fcdd888b8e3bcda68ccf95141963b0edba89f573d476fec75d6cc8e12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeIops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSize")
    def ebs_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeSize"))

    @ebs_volume_size.setter
    def ebs_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbce9dc31f1e434e04b32cdcb172d404c8de2383783454213f2aba06c0259026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughput")
    def ebs_volume_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeThroughput"))

    @ebs_volume_throughput.setter
    def ebs_volume_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27641e6cac4d444c85cf8048ecccc46dd9a438e21c73d4c5074e44f35412c543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeType")
    def ebs_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ebsVolumeType"))

    @ebs_volume_type.setter
    def ebs_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8715d251b43cff2f181f206eff29a7c66f02fc70b8fd29a462ce5c2b6c8aa941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9661a8baebc9d3542398c5d60f842bffeec5bff6d1b18316070cc753762eab77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__205658f1d48b8ec9a79e05345ff57cd1e0a3f77d61b49614e4bfd35c6b2863e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercent")
    def spot_bid_price_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidPricePercent"))

    @spot_bid_price_percent.setter
    def spot_bid_price_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99699544b0536ac9af36b5c9206b8751e32cbb9dbf443892e76b2d45ab9a678)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidPricePercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d57abe78ba872b6ccc229467303ebc36db9c5d86ac5e85265c4a0e1577f75bf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d371501dae8e0a1cf30226302f232fd4b2e30b4cedf3bc920ba28bc24fff9f80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAzureAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "first_on_demand": "firstOnDemand",
        "log_analytics_info": "logAnalyticsInfo",
        "spot_bid_max_price": "spotBidMaxPrice",
    },
)
class DataDatabricksClusterClusterInfoSpecAzureAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.
        '''
        if isinstance(log_analytics_info, dict):
            log_analytics_info = DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo(**log_analytics_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9dfbdbbb261897455d062be8fd8ae6b4d8fd4fe8149d030ac1b8c9af6b0f031)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument log_analytics_info", value=log_analytics_info, expected_type=type_hints["log_analytics_info"])
            check_type(argname="argument spot_bid_max_price", value=spot_bid_max_price, expected_type=type_hints["spot_bid_max_price"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if log_analytics_info is not None:
            self._values["log_analytics_info"] = log_analytics_info
        if spot_bid_max_price is not None:
            self._values["spot_bid_max_price"] = spot_bid_max_price

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_analytics_info(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo"]:
        '''log_analytics_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        '''
        result = self._values.get("log_analytics_info")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo"], result)

    @builtins.property
    def spot_bid_max_price(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.'''
        result = self._values.get("spot_bid_max_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecAzureAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo",
    jsii_struct_bases=[],
    name_mapping={
        "log_analytics_primary_key": "logAnalyticsPrimaryKey",
        "log_analytics_workspace_id": "logAnalyticsWorkspaceId",
    },
)
class DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo:
    def __init__(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d322ff24ada47ee39a352a5c3a7a54697ed45cdc7eeb3a778f299128c80931a0)
            check_type(argname="argument log_analytics_primary_key", value=log_analytics_primary_key, expected_type=type_hints["log_analytics_primary_key"])
            check_type(argname="argument log_analytics_workspace_id", value=log_analytics_workspace_id, expected_type=type_hints["log_analytics_workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_analytics_primary_key is not None:
            self._values["log_analytics_primary_key"] = log_analytics_primary_key
        if log_analytics_workspace_id is not None:
            self._values["log_analytics_workspace_id"] = log_analytics_workspace_id

    @builtins.property
    def log_analytics_primary_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.'''
        result = self._values.get("log_analytics_primary_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_analytics_workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.'''
        result = self._values.get("log_analytics_workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__04ec981d3bccdd0bcbe28342833170660bca4448c7aa4eed78fb24c0112dac9c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLogAnalyticsPrimaryKey")
    def reset_log_analytics_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsPrimaryKey", []))

    @jsii.member(jsii_name="resetLogAnalyticsWorkspaceId")
    def reset_log_analytics_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKeyInput")
    def log_analytics_primary_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsPrimaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceIdInput")
    def log_analytics_workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsWorkspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKey")
    def log_analytics_primary_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsPrimaryKey"))

    @log_analytics_primary_key.setter
    def log_analytics_primary_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__851427dd6f70bb698a1fc4b632b3b058743f9b06ba343a396ee8dfd3e99641bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsPrimaryKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceId")
    def log_analytics_workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsWorkspaceId"))

    @log_analytics_workspace_id.setter
    def log_analytics_workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea37fad338206e178576866bba82f8e1987f1ee18d300d1c2c527a5263dd2af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab26c9040e90d7e9d9f7f56becac300bc083bc671fde52fb13c2209e283ae01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecAzureAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecAzureAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69640d1350917ccf2cf1a742e1a3520ed6453ed2a8da8ecc139d8419446c1150)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLogAnalyticsInfo")
    def put_log_analytics_info(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_primary_key DataDatabricksCluster#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_workspace_id DataDatabricksCluster#log_analytics_workspace_id}.
        '''
        value = DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo(
            log_analytics_primary_key=log_analytics_primary_key,
            log_analytics_workspace_id=log_analytics_workspace_id,
        )

        return typing.cast(None, jsii.invoke(self, "putLogAnalyticsInfo", [value]))

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetLogAnalyticsInfo")
    def reset_log_analytics_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsInfo", []))

    @jsii.member(jsii_name="resetSpotBidMaxPrice")
    def reset_spot_bid_max_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidMaxPrice", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfo")
    def log_analytics_info(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfoOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfoOutputReference, jsii.get(self, "logAnalyticsInfo"))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfoInput")
    def log_analytics_info_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo], jsii.get(self, "logAnalyticsInfoInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__fb39c8f68bd724f218d79e88c6ef0343ad59152a2a3dbd489d99ff879bde5da3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa67299c3a9d3548912482cc879bb8793247689a83aa08cb4b9e381b52564603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPrice")
    def spot_bid_max_price(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidMaxPrice"))

    @spot_bid_max_price.setter
    def spot_bid_max_price(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c35ba8591ef635a8761eb997006d11e4b8ac4dd20478c2294e4c6e4ee9545d20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidMaxPrice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c941064a46dd7864bb83752399a4b3db8a58eec2f0ad7ec5a996d5e1c6d215e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConf",
    jsii_struct_bases=[],
    name_mapping={"dbfs": "dbfs", "s3": "s3", "volumes": "volumes"},
)
class DataDatabricksClusterClusterInfoSpecClusterLogConf:
    def __init__(
        self,
        *,
        dbfs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecClusterLogConfS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        if isinstance(dbfs, dict):
            dbfs = DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs(**dbfs)
        if isinstance(s3, dict):
            s3 = DataDatabricksClusterClusterInfoSpecClusterLogConfS3(**s3)
        if isinstance(volumes, dict):
            volumes = DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes(**volumes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a13616daf4806496e2e9fa7b381464c0d7dcb4bda905a86547de6a23e6636f7d)
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def dbfs(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs"], result)

    @builtins.property
    def s3(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfS3"], result)

    @builtins.property
    def volumes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterLogConf(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b584e866f92c444042fd00b721c885132dd48f4709c6b6f39ea3f8bdc0795089)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecClusterLogConfDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e67e62f77f6aa9cc5f1f8e55ed9412b07de9aa1feb9c5f4b32874274699f5cfd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaaedd79eff9704bdbe996eafa01b2f9c2928c413f0d01b3aca6a5157c2c7620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e43525d56ee4d9194800d4bda307b99daa2a90a47dcc222e8948f9a0516335a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecClusterLogConfOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6081c454939049b69b508f7cfd467371730d208bd55d54511dded64dcfc77f9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        value = DataDatabricksClusterClusterInfoSpecClusterLogConfS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecClusterLogConfDbfsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecClusterLogConfDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecClusterLogConfS3OutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecClusterLogConfS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecClusterLogConfVolumesOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecClusterLogConfVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfS3"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bf0a5858abe66cf0e0e9b418633742e47eb068e87396f54ab58581c1b28b4f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class DataDatabricksClusterClusterInfoSpecClusterLogConfS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbc8a9cd5ae7bdd68bebcbd75070bc1490d1f643ef56e5fa367f249ad67dd71)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterLogConfS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecClusterLogConfS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5926873969070e217c7516c20da6cb6c0744aeb43fcc097cb8d1088fb3de052c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccf6d29d630861046bf42c93dcfce9b939bba2300440edb80a22ddf725cfe16e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fc2adbf614ea5bf7a9d312e5e1b0fca6bde00239126d374141ac29d426113b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba67f57d94a36bebb17fe4271887d4c5b1cb6c2374eed2548efdc5b05617e87a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cac116ee8ee76f6ccc063ebe31dc594fb170f87fe75b643228b755845836cd6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699b4ab2a10f83685afa598c79494b8d4b248d6bb77c4135f3c42b04eb3a2ba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02a59624879210257dde9af201beccfe07e03ed86f74a7ee74b8ce687f1f1475)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54f3ce9530f109cfd67b53874092e3b4f7523b1f4b02edb998680b814ea22542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfS3]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d69cd3a0b6824cc168ec7a606d216b5c0da6577cb44de0415b6de5fda3d96ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95edc15e4d409c36b975d55d0d55bd44ebc0ff11bed85d4fe685a675d5e0b30)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecClusterLogConfVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterLogConfVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b658517c1fc0fcaf6fd37fde88596c31ed3138c3308da2da12fe1133601b6f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41950f1440c31374d5c3002bb9ac86cc7b312f2078a7170d9f994e927fd80635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ee0931be92584250f0e6240e90e6846feefb518568704562f1cda2d20feea7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterMountInfo",
    jsii_struct_bases=[],
    name_mapping={
        "local_mount_dir_path": "localMountDirPath",
        "network_filesystem_info": "networkFilesystemInfo",
        "remote_mount_dir_path": "remoteMountDirPath",
    },
)
class DataDatabricksClusterClusterInfoSpecClusterMountInfo:
    def __init__(
        self,
        *,
        local_mount_dir_path: builtins.str,
        network_filesystem_info: typing.Union["DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo", typing.Dict[builtins.str, typing.Any]],
        remote_mount_dir_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param local_mount_dir_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_mount_dir_path DataDatabricksCluster#local_mount_dir_path}.
        :param network_filesystem_info: network_filesystem_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#network_filesystem_info DataDatabricksCluster#network_filesystem_info}
        :param remote_mount_dir_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_mount_dir_path DataDatabricksCluster#remote_mount_dir_path}.
        '''
        if isinstance(network_filesystem_info, dict):
            network_filesystem_info = DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo(**network_filesystem_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b488567b953c2815a335abdbe68f30e01865bca02f880e5ea64a6677d20f84a2)
            check_type(argname="argument local_mount_dir_path", value=local_mount_dir_path, expected_type=type_hints["local_mount_dir_path"])
            check_type(argname="argument network_filesystem_info", value=network_filesystem_info, expected_type=type_hints["network_filesystem_info"])
            check_type(argname="argument remote_mount_dir_path", value=remote_mount_dir_path, expected_type=type_hints["remote_mount_dir_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "local_mount_dir_path": local_mount_dir_path,
            "network_filesystem_info": network_filesystem_info,
        }
        if remote_mount_dir_path is not None:
            self._values["remote_mount_dir_path"] = remote_mount_dir_path

    @builtins.property
    def local_mount_dir_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_mount_dir_path DataDatabricksCluster#local_mount_dir_path}.'''
        result = self._values.get("local_mount_dir_path")
        assert result is not None, "Required property 'local_mount_dir_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_filesystem_info(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo":
        '''network_filesystem_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#network_filesystem_info DataDatabricksCluster#network_filesystem_info}
        '''
        result = self._values.get("network_filesystem_info")
        assert result is not None, "Required property 'network_filesystem_info' is missing"
        return typing.cast("DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo", result)

    @builtins.property
    def remote_mount_dir_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#remote_mount_dir_path DataDatabricksCluster#remote_mount_dir_path}.'''
        result = self._values.get("remote_mount_dir_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterMountInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecClusterMountInfoList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterMountInfoList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0ade1ec3bf5f49ac641d2c2e2409f58b210183dba6bfd726e9259d504ff79ee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksClusterClusterInfoSpecClusterMountInfoOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89041ab7aa69f0f0ac157416e5db117bacd70e5ce63e9fb6f98c40c8cd5e4d30)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksClusterClusterInfoSpecClusterMountInfoOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c174feb0bee63bd9df97b6faef16926ecfcc7c67f258ee4cea2a258ca286cbec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c60deae8cf1f5e042226c3637f6de8e57716649b4e0c36c7a32077339e52a20a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d841f3bad4834ee7b51f22218b4f5b7d3f387ed0ad8802c6fa7c2caef6b8cc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad071a800f9f3bac3a5cc6c70ec74734a38667de042b3e6d509e03bb3c933e77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo",
    jsii_struct_bases=[],
    name_mapping={"server_address": "serverAddress", "mount_options": "mountOptions"},
)
class DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo:
    def __init__(
        self,
        *,
        server_address: builtins.str,
        mount_options: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#server_address DataDatabricksCluster#server_address}.
        :param mount_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#mount_options DataDatabricksCluster#mount_options}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1043c04f70eb880b8ac74a73a12d43654154aac875c06d6d658675bfee8cf109)
            check_type(argname="argument server_address", value=server_address, expected_type=type_hints["server_address"])
            check_type(argname="argument mount_options", value=mount_options, expected_type=type_hints["mount_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "server_address": server_address,
        }
        if mount_options is not None:
            self._values["mount_options"] = mount_options

    @builtins.property
    def server_address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#server_address DataDatabricksCluster#server_address}.'''
        result = self._values.get("server_address")
        assert result is not None, "Required property 'server_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount_options(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#mount_options DataDatabricksCluster#mount_options}.'''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__971664711a9be665b563f37cad1a3c1e72e9a098db040431d37dc715709e3664)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMountOptions")
    def reset_mount_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountOptions", []))

    @builtins.property
    @jsii.member(jsii_name="mountOptionsInput")
    def mount_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mountOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="serverAddressInput")
    def server_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="mountOptions")
    def mount_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountOptions"))

    @mount_options.setter
    def mount_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a7e1376a05ae5f34375b918e9f8b030016203e0cfef2096267098a5d0860a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mountOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverAddress")
    def server_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverAddress"))

    @server_address.setter
    def server_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__019fafd26c8b88e32112d037c2c6cbfee7aaed6a67045f2dfade18a6f144bb68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fbdad5c1705d4bc0bdffedfc6549a3cf2c379036c44a197e1e99a7e1aca614b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecClusterMountInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecClusterMountInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__678c553415ca85e9685f4d7aeb23dc77d9fbec5dc848cd148fa778088f6f0349)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNetworkFilesystemInfo")
    def put_network_filesystem_info(
        self,
        *,
        server_address: builtins.str,
        mount_options: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#server_address DataDatabricksCluster#server_address}.
        :param mount_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#mount_options DataDatabricksCluster#mount_options}.
        '''
        value = DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo(
            server_address=server_address, mount_options=mount_options
        )

        return typing.cast(None, jsii.invoke(self, "putNetworkFilesystemInfo", [value]))

    @jsii.member(jsii_name="resetRemoteMountDirPath")
    def reset_remote_mount_dir_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteMountDirPath", []))

    @builtins.property
    @jsii.member(jsii_name="networkFilesystemInfo")
    def network_filesystem_info(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfoOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfoOutputReference, jsii.get(self, "networkFilesystemInfo"))

    @builtins.property
    @jsii.member(jsii_name="localMountDirPathInput")
    def local_mount_dir_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localMountDirPathInput"))

    @builtins.property
    @jsii.member(jsii_name="networkFilesystemInfoInput")
    def network_filesystem_info_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo], jsii.get(self, "networkFilesystemInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteMountDirPathInput")
    def remote_mount_dir_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "remoteMountDirPathInput"))

    @builtins.property
    @jsii.member(jsii_name="localMountDirPath")
    def local_mount_dir_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localMountDirPath"))

    @local_mount_dir_path.setter
    def local_mount_dir_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87e1803af40ddf249b38af8269ab0e474b032c08bb948fffd8225fd739ee917a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localMountDirPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteMountDirPath")
    def remote_mount_dir_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteMountDirPath"))

    @remote_mount_dir_path.setter
    def remote_mount_dir_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a26ce217fd2fb4c8aa59fc807f54381fe69aa3c47e615092da948d6720eff01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteMountDirPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecClusterMountInfo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecClusterMountInfo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecClusterMountInfo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__375a3f0ec5de7c5d7f7328b2eb6271d71b8d7aaf20ebcc5f7797c02b32a56b45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecDockerImage",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "basic_auth": "basicAuth"},
)
class DataDatabricksClusterClusterInfoSpecDockerImage:
    def __init__(
        self,
        *,
        url: builtins.str,
        basic_auth: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        '''
        if isinstance(basic_auth, dict):
            basic_auth = DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e002673d5c4f56c140c1c9b6a81cc14d8d1ff2359fa6da69a6e0b8609f5b83)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth"]:
        '''basic_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecDockerImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28a2772f604a884df9f5f7e36c0ddf4ce2e55a19db83250164727b94a0970631)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecDockerImageBasicAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecDockerImageBasicAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__43404cd7cb1b15cffce1e1f4772e39c3a40fb9af6fd15cb619de33c5425d276e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28656ddd600d5c6f795ac61e37ffc64b874df88660289d016f82ddacab68bf78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f362c187effef6217134fe8f395dd23d0089c76ebf35873964f74c62633f0c52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e74ebc54a764f156cbca18c777799ab6f3cd416ec91014c72d70d975f2f0fd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecDockerImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecDockerImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dafb4fe145488329c4631ba2ae3abcc0817b4ea0b1826d5978325288c4d44835)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBasicAuth")
    def put_basic_auth(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#password DataDatabricksCluster#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#username DataDatabricksCluster#username}.
        '''
        value = DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth(
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
    ) -> DataDatabricksClusterClusterInfoSpecDockerImageBasicAuthOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecDockerImageBasicAuthOutputReference, jsii.get(self, "basicAuth"))

    @builtins.property
    @jsii.member(jsii_name="basicAuthInput")
    def basic_auth_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth], jsii.get(self, "basicAuthInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__9a44f60a5d1e4c29b7d0695ae55caeb71181f942a70ef19f38177b5f06b0d541)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e309f9d0da33507cd7789902afab655b20b028cf8d96f2d0433dadd900d70530)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecGcpAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "boot_disk_size": "bootDiskSize",
        "first_on_demand": "firstOnDemand",
        "google_service_account": "googleServiceAccount",
        "local_ssd_count": "localSsdCount",
        "use_preemptible_executors": "usePreemptibleExecutors",
        "zone_id": "zoneId",
    },
)
class DataDatabricksClusterClusterInfoSpecGcpAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        boot_disk_size: typing.Optional[jsii.Number] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param boot_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.
        :param use_preemptible_executors: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14fac0c0add21dfe40649adbb3775cade361afe5ee3841b2c683922e009cddcf)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument boot_disk_size", value=boot_disk_size, expected_type=type_hints["boot_disk_size"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument google_service_account", value=google_service_account, expected_type=type_hints["google_service_account"])
            check_type(argname="argument local_ssd_count", value=local_ssd_count, expected_type=type_hints["local_ssd_count"])
            check_type(argname="argument use_preemptible_executors", value=use_preemptible_executors, expected_type=type_hints["use_preemptible_executors"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if boot_disk_size is not None:
            self._values["boot_disk_size"] = boot_disk_size
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if google_service_account is not None:
            self._values["google_service_account"] = google_service_account
        if local_ssd_count is not None:
            self._values["local_ssd_count"] = local_ssd_count
        if use_preemptible_executors is not None:
            self._values["use_preemptible_executors"] = use_preemptible_executors
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def boot_disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.'''
        result = self._values.get("boot_disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def google_service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.'''
        result = self._values.get("google_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def use_preemptible_executors(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.'''
        result = self._values.get("use_preemptible_executors")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecGcpAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecGcpAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecGcpAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e8ade5869e96e985c0680614d9ff55059205e67039c3bc146d166d4851cef09)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetBootDiskSize")
    def reset_boot_disk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDiskSize", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetGoogleServiceAccount")
    def reset_google_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleServiceAccount", []))

    @jsii.member(jsii_name="resetLocalSsdCount")
    def reset_local_ssd_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSsdCount", []))

    @jsii.member(jsii_name="resetUsePreemptibleExecutors")
    def reset_use_preemptible_executors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePreemptibleExecutors", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDiskSizeInput")
    def boot_disk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bootDiskSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccountInput")
    def google_service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="localSsdCountInput")
    def local_ssd_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localSsdCountInput"))

    @builtins.property
    @jsii.member(jsii_name="usePreemptibleExecutorsInput")
    def use_preemptible_executors_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePreemptibleExecutorsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__fbca10cfd16397db3799cd5b99d49f670c68238668d187198bcab0246473fb4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootDiskSize")
    def boot_disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootDiskSize"))

    @boot_disk_size.setter
    def boot_disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dba0cf795371350e1ebbc8b1d1499984130bea81c166a221c5a94d94d6df54e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootDiskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31fc48287278156551bf20ea688291972ac51f88ec3e98cb7a730c93837af70b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccount")
    def google_service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "googleServiceAccount"))

    @google_service_account.setter
    def google_service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad077c7f3e4d3770be19cda356d11a0ef04152de0519337a3c0b86552babd132)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleServiceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a06d9bb4a6e648c98ee4564f3d007fde3f16594dd8e6bb11a1008d8acb1c1c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePreemptibleExecutors")
    def use_preemptible_executors(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePreemptibleExecutors"))

    @use_preemptible_executors.setter
    def use_preemptible_executors(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e93f5fc257960aa45d71155b29b1742f4faa8c5ad9c0894c74e8b5393103978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePreemptibleExecutors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__583f521ee2ac83d6de154c30823a3dc912321774ce7f8f795a435a8b88ccedd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b3665d18d18eacf5efa6161143ad4d38ccf6f88ea64c706d5c52c2d34d3711)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScripts",
    jsii_struct_bases=[],
    name_mapping={
        "abfss": "abfss",
        "dbfs": "dbfs",
        "file": "file",
        "gcs": "gcs",
        "s3": "s3",
        "volumes": "volumes",
        "workspace": "workspace",
    },
)
class DataDatabricksClusterClusterInfoSpecInitScripts:
    def __init__(
        self,
        *,
        abfss: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsAbfss", typing.Dict[builtins.str, typing.Any]]] = None,
        dbfs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        file: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsFile", typing.Dict[builtins.str, typing.Any]]] = None,
        gcs: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsGcs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param abfss: abfss block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#abfss DataDatabricksCluster#abfss}
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param file: file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#file DataDatabricksCluster#file}
        :param gcs: gcs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcs DataDatabricksCluster#gcs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        :param workspace: workspace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workspace DataDatabricksCluster#workspace}
        '''
        if isinstance(abfss, dict):
            abfss = DataDatabricksClusterClusterInfoSpecInitScriptsAbfss(**abfss)
        if isinstance(dbfs, dict):
            dbfs = DataDatabricksClusterClusterInfoSpecInitScriptsDbfs(**dbfs)
        if isinstance(file, dict):
            file = DataDatabricksClusterClusterInfoSpecInitScriptsFile(**file)
        if isinstance(gcs, dict):
            gcs = DataDatabricksClusterClusterInfoSpecInitScriptsGcs(**gcs)
        if isinstance(s3, dict):
            s3 = DataDatabricksClusterClusterInfoSpecInitScriptsS3(**s3)
        if isinstance(volumes, dict):
            volumes = DataDatabricksClusterClusterInfoSpecInitScriptsVolumes(**volumes)
        if isinstance(workspace, dict):
            workspace = DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace(**workspace)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef31b7a6d03d8f598e1209dd9ed7ec231c05098571f6ebebe07bc341fd2df14a)
            check_type(argname="argument abfss", value=abfss, expected_type=type_hints["abfss"])
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument gcs", value=gcs, expected_type=type_hints["gcs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
            check_type(argname="argument workspace", value=workspace, expected_type=type_hints["workspace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if abfss is not None:
            self._values["abfss"] = abfss
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if file is not None:
            self._values["file"] = file
        if gcs is not None:
            self._values["gcs"] = gcs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes
        if workspace is not None:
            self._values["workspace"] = workspace

    @builtins.property
    def abfss(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsAbfss"]:
        '''abfss block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#abfss DataDatabricksCluster#abfss}
        '''
        result = self._values.get("abfss")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsAbfss"], result)

    @builtins.property
    def dbfs(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsDbfs"], result)

    @builtins.property
    def file(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsFile"]:
        '''file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#file DataDatabricksCluster#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsFile"], result)

    @builtins.property
    def gcs(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsGcs"]:
        '''gcs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#gcs DataDatabricksCluster#gcs}
        '''
        result = self._values.get("gcs")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsGcs"], result)

    @builtins.property
    def s3(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsS3"], result)

    @builtins.property
    def volumes(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsVolumes"], result)

    @builtins.property
    def workspace(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace"]:
        '''workspace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#workspace DataDatabricksCluster#workspace}
        '''
        result = self._values.get("workspace")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScripts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsAbfss",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsAbfss:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__426ae4d552d798c02d723f8dd7ccba0b3c001456ca4b4d40c1222ccfb84a9ba4)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsAbfss(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsAbfssOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsAbfssOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e1fd179941591e034f52d4ed908773d5a2069bef943748eb2582f5f509d40ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427b01852378d673a0a96026976176347d9179620181c255b33acd0ee1c5156e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f0c6292d959ff42606b88c5df4df20ad232d191596e71eb0a0854b631e47b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__342a2b00c9fb0cdfc8d5e5d528af13ab4c86e62d0d9b665551b3db9f4bf60f07)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4eb22efb0a36de0f60c2b16f7a3565b5f95744a0f2b8ba93fe61935716dc1416)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__928375090663b972dc99c916ee04aa8b361b016fb888b0e2d4c00a0eea60a553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__042da1ee9a729226449d9a9d6c9a84f3849ff65687200df29c5ae29ac5716ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsFile",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsFile:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a046ae6c44e52b2379874535ae4a3bbebc3e9ce4f3f38c6c4169dbb74347237e)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__204208e7c129e91b12196ad1aedd4224618d9848e4764b76aad6da4902a872ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__800cd806c83775690b8ea7352e436c78bac30dffc1690b022389be37c2f29828)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69f62d81a5aa08c07c2574ff8e2f52d30c1c7f86a6f41086dcd45ad908fa8d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsGcs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsGcs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3bd930035d28dceceb7a2348a0e7f76b0aa875d038dc919b7c3b1dd372c633d)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsGcs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsGcsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsGcsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a26df2e984722355e9e45982a775b04c9c652247ca802f1a374130488c241555)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab5534cc5ecabd38bad8512058217aff82e4143dba181ba2ae26c0e809373619)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cab1659ada805ed4b6ede430145f0b1ae5410378229651fd3040656a02acd3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecInitScriptsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4c103b13acecf83d2460523b7c70f5309f4c7cd20f613ee51c357916567248a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksClusterClusterInfoSpecInitScriptsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57cb160fc595ebdd5635763bb9e54f31da16cf64e7d34c68cca54f87fcb24f1f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksClusterClusterInfoSpecInitScriptsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d5b9bac118fbcaef4ed2c347b2c5f92c3e1d3e53a6f0f1ac8dcfd709f8f0ce6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05108bc2ff682ad25bcfd889faa1afa9c2ed5de249f8ba233121e6b3ea03e8d4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8849a6f5b9830d3ed6e18900ab16096a2e18902e2527bea12772c764675be8db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__285fe8e1a904370a527cdbd9cf90d1233843027f49a4fed172b6ae4ab56f612c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecInitScriptsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7bc56e69d88c620999c459800f87e6b2df32d5060e7eb0086802704512d29a0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAbfss")
    def put_abfss(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsAbfss(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putAbfss", [value]))

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsDbfs(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putFile")
    def put_file(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsFile(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putFile", [value]))

    @jsii.member(jsii_name="putGcs")
    def put_gcs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsGcs(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putGcs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsVolumes(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="putWorkspace")
    def put_workspace(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        value = DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace(
            destination=destination
        )

        return typing.cast(None, jsii.invoke(self, "putWorkspace", [value]))

    @jsii.member(jsii_name="resetAbfss")
    def reset_abfss(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbfss", []))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetFile")
    def reset_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFile", []))

    @jsii.member(jsii_name="resetGcs")
    def reset_gcs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @jsii.member(jsii_name="resetWorkspace")
    def reset_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspace", []))

    @builtins.property
    @jsii.member(jsii_name="abfss")
    def abfss(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecInitScriptsAbfssOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecInitScriptsAbfssOutputReference, jsii.get(self, "abfss"))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecInitScriptsDbfsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecInitScriptsDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="file")
    def file(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecInitScriptsFileOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecInitScriptsFileOutputReference, jsii.get(self, "file"))

    @builtins.property
    @jsii.member(jsii_name="gcs")
    def gcs(self) -> DataDatabricksClusterClusterInfoSpecInitScriptsGcsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecInitScriptsGcsOutputReference, jsii.get(self, "gcs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(self) -> "DataDatabricksClusterClusterInfoSpecInitScriptsS3OutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecInitScriptsS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecInitScriptsVolumesOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecInitScriptsVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="workspace")
    def workspace(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecInitScriptsWorkspaceOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecInitScriptsWorkspaceOutputReference", jsii.get(self, "workspace"))

    @builtins.property
    @jsii.member(jsii_name="abfssInput")
    def abfss_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss], jsii.get(self, "abfssInput"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="fileInput")
    def file_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile], jsii.get(self, "fileInput"))

    @builtins.property
    @jsii.member(jsii_name="gcsInput")
    def gcs_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs], jsii.get(self, "gcsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsS3"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsVolumes"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceInput")
    def workspace_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace"], jsii.get(self, "workspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecInitScripts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecInitScripts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecInitScripts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a67aa60ddcd67222e28e3312f007cbb2e7e9a786ca567c0b14c56c71d85e7e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class DataDatabricksClusterClusterInfoSpecInitScriptsS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e69fb16b3e54298324de65ef683c79c9bc8652d2f4296d4fb2c76a348174b350)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#canned_acl DataDatabricksCluster#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#enable_encryption DataDatabricksCluster#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#encryption_type DataDatabricksCluster#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#endpoint DataDatabricksCluster#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#kms_key DataDatabricksCluster#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#region DataDatabricksCluster#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed399b83585e5b5ac781642a68b1c126ce1ef0a1bf3221d4b8efe38f7b282845)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5ee8352ca43b98eb85ca98226217d321e17ba905e666b9dd51daaa5da91f42d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a17043b1530995cf79ae38d43ceedfd455f83aef5751418d397fd55bd061a0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0223b1d1aee7fb13b711a49a84e8f8e7608f556263bdea0b9db3f850c205f9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ff4f3f099f9b3bbd90aec96219a889318f6791e0928659c863a54a80ae03ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48bbb3a24738023a33e93952311d5339b268d395af8f30125b761a1005b30cac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f508b012e37f2d6640a4bc2533beda57770065d66e529afe921c2b0e75741a65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d91c3293ffcbeb200ee3b4031ae53e537b3ab8ac98c477e02454478a9f0c51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsS3]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d889bffa51104254b479536655f38a443dbdedc8d7849a9d1efecf3d8278fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__951cadf515dbf9838ae801ce297d01bae7ed599659932bced6318fa03daa6c26)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0630614bf797ace9f8120388cd2468b63b2ce3de5a1dba761ee85d5406e4f4d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4487424b01decb9e316bb962b9b081ce11035ff2862fd704fff22325f484e321)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsVolumes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d2137797a838b7f4471bb58301423d2ab5e1bd9411a4e1ed3488af0ab6b9556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e180051c7101bdb272871950e7ac2a2e64df9de6228ae5c7aa7cb415cbca1940)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#destination DataDatabricksCluster#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecInitScriptsWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecInitScriptsWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__700ffd105995af2b9e0ed98b43a4af3bc7542fb8274b58c11c12741e8da0c600)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c853e8710017bf51e138b654cca4f25a2a38e3d075da492b78ce4195f565ca08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9fc22dd440e97085a39364b253a8b6cb4534cf481403775c5427182c89b4a3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibrary",
    jsii_struct_bases=[],
    name_mapping={
        "cran": "cran",
        "egg": "egg",
        "jar": "jar",
        "maven": "maven",
        "pypi": "pypi",
        "requirements": "requirements",
        "whl": "whl",
    },
)
class DataDatabricksClusterClusterInfoSpecLibrary:
    def __init__(
        self,
        *,
        cran: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecLibraryCran", typing.Dict[builtins.str, typing.Any]]] = None,
        egg: typing.Optional[builtins.str] = None,
        jar: typing.Optional[builtins.str] = None,
        maven: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecLibraryMaven", typing.Dict[builtins.str, typing.Any]]] = None,
        pypi: typing.Optional[typing.Union["DataDatabricksClusterClusterInfoSpecLibraryPypi", typing.Dict[builtins.str, typing.Any]]] = None,
        requirements: typing.Optional[builtins.str] = None,
        whl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cran: cran block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cran DataDatabricksCluster#cran}
        :param egg: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#egg DataDatabricksCluster#egg}.
        :param jar: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jar DataDatabricksCluster#jar}.
        :param maven: maven block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#maven DataDatabricksCluster#maven}
        :param pypi: pypi block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#pypi DataDatabricksCluster#pypi}
        :param requirements: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#requirements DataDatabricksCluster#requirements}.
        :param whl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#whl DataDatabricksCluster#whl}.
        '''
        if isinstance(cran, dict):
            cran = DataDatabricksClusterClusterInfoSpecLibraryCran(**cran)
        if isinstance(maven, dict):
            maven = DataDatabricksClusterClusterInfoSpecLibraryMaven(**maven)
        if isinstance(pypi, dict):
            pypi = DataDatabricksClusterClusterInfoSpecLibraryPypi(**pypi)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a8d7e81d9f48a581d582f69bf6729ea88c96e9db17b081076547dd696430da)
            check_type(argname="argument cran", value=cran, expected_type=type_hints["cran"])
            check_type(argname="argument egg", value=egg, expected_type=type_hints["egg"])
            check_type(argname="argument jar", value=jar, expected_type=type_hints["jar"])
            check_type(argname="argument maven", value=maven, expected_type=type_hints["maven"])
            check_type(argname="argument pypi", value=pypi, expected_type=type_hints["pypi"])
            check_type(argname="argument requirements", value=requirements, expected_type=type_hints["requirements"])
            check_type(argname="argument whl", value=whl, expected_type=type_hints["whl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cran is not None:
            self._values["cran"] = cran
        if egg is not None:
            self._values["egg"] = egg
        if jar is not None:
            self._values["jar"] = jar
        if maven is not None:
            self._values["maven"] = maven
        if pypi is not None:
            self._values["pypi"] = pypi
        if requirements is not None:
            self._values["requirements"] = requirements
        if whl is not None:
            self._values["whl"] = whl

    @builtins.property
    def cran(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryCran"]:
        '''cran block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cran DataDatabricksCluster#cran}
        '''
        result = self._values.get("cran")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryCran"], result)

    @builtins.property
    def egg(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#egg DataDatabricksCluster#egg}.'''
        result = self._values.get("egg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jar(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jar DataDatabricksCluster#jar}.'''
        result = self._values.get("jar")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryMaven"]:
        '''maven block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#maven DataDatabricksCluster#maven}
        '''
        result = self._values.get("maven")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryMaven"], result)

    @builtins.property
    def pypi(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryPypi"]:
        '''pypi block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#pypi DataDatabricksCluster#pypi}
        '''
        result = self._values.get("pypi")
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryPypi"], result)

    @builtins.property
    def requirements(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#requirements DataDatabricksCluster#requirements}.'''
        result = self._values.get("requirements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def whl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#whl DataDatabricksCluster#whl}.'''
        result = self._values.get("whl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecLibrary(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryCran",
    jsii_struct_bases=[],
    name_mapping={"package": "package", "repo": "repo"},
)
class DataDatabricksClusterClusterInfoSpecLibraryCran:
    def __init__(
        self,
        *,
        package: builtins.str,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param package: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98a1679f7867886515aa0766bed07cdd815d7cfa076ceb4d4062f86562b56fb)
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "package": package,
        }
        if repo is not None:
            self._values["repo"] = repo

    @builtins.property
    def package(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.'''
        result = self._values.get("package")
        assert result is not None, "Required property 'package' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.'''
        result = self._values.get("repo")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecLibraryCran(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecLibraryCranOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryCranOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a5b98994c0e1d1e5e9a2a4d3490cad030c67f6f3928b6059dae3462552552d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRepo")
    def reset_repo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepo", []))

    @builtins.property
    @jsii.member(jsii_name="packageInput")
    def package_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "packageInput"))

    @builtins.property
    @jsii.member(jsii_name="repoInput")
    def repo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoInput"))

    @builtins.property
    @jsii.member(jsii_name="package")
    def package(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "package"))

    @package.setter
    def package(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a491fe354940615b4a9de7a7c568a20977dec1e4fefd08b84bbfd55c1bd27ff7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "package", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repo")
    def repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repo"))

    @repo.setter
    def repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e16d0e9d004748376dbeb3fd82b06923a2f360c97d6394eeb28dda7dd0eb0d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11fe85067d65182ce692427b5ae4e9161a86041af610891bea4cde22412b4546)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecLibraryList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__099be35d5268d1d9ed68b5b506dd8cc23b590135b2b9c047b0b9a99246a78277)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksClusterClusterInfoSpecLibraryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6f15388dc583e0021b3459ca1c945e2014799934bb75654327283dfd1aa1c0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksClusterClusterInfoSpecLibraryOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46a2dbc4b1c50ea7b6eba7a1aff20f130e9cb81f1d0d3138ebcd56e708b3b12)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58fb0a783d34dc295f3bee4022cbc001be80408f0c5949f6ab1c6fa914988a6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9db4bb9eb94585dad51ace85b17aeda99b91b8904bad42567a235b16782199a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a02f482cd6a0623bed6917277b24f21798d1c150d03fca0beda5867b4b61af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryMaven",
    jsii_struct_bases=[],
    name_mapping={
        "coordinates": "coordinates",
        "exclusions": "exclusions",
        "repo": "repo",
    },
)
class DataDatabricksClusterClusterInfoSpecLibraryMaven:
    def __init__(
        self,
        *,
        coordinates: builtins.str,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param coordinates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#coordinates DataDatabricksCluster#coordinates}.
        :param exclusions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#exclusions DataDatabricksCluster#exclusions}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c2dc804369a59330421c5ec70bb6ef5d12de204333e7f6bc27bac6ffc026df1)
            check_type(argname="argument coordinates", value=coordinates, expected_type=type_hints["coordinates"])
            check_type(argname="argument exclusions", value=exclusions, expected_type=type_hints["exclusions"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "coordinates": coordinates,
        }
        if exclusions is not None:
            self._values["exclusions"] = exclusions
        if repo is not None:
            self._values["repo"] = repo

    @builtins.property
    def coordinates(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#coordinates DataDatabricksCluster#coordinates}.'''
        result = self._values.get("coordinates")
        assert result is not None, "Required property 'coordinates' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#exclusions DataDatabricksCluster#exclusions}.'''
        result = self._values.get("exclusions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repo(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.'''
        result = self._values.get("repo")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecLibraryMaven(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecLibraryMavenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryMavenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f71dcc43b3905dc2f41ff4afbee7e67bfeb5dd6a135805f8cfb4546ee77e1de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExclusions")
    def reset_exclusions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclusions", []))

    @jsii.member(jsii_name="resetRepo")
    def reset_repo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepo", []))

    @builtins.property
    @jsii.member(jsii_name="coordinatesInput")
    def coordinates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coordinatesInput"))

    @builtins.property
    @jsii.member(jsii_name="exclusionsInput")
    def exclusions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclusionsInput"))

    @builtins.property
    @jsii.member(jsii_name="repoInput")
    def repo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoInput"))

    @builtins.property
    @jsii.member(jsii_name="coordinates")
    def coordinates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coordinates"))

    @coordinates.setter
    def coordinates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae0cb8dd60eb48040723067051ac773eaaf966f665eb23ac8bba24f9e7a6706)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coordinates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclusions"))

    @exclusions.setter
    def exclusions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a0f68c7cc405442eb8c4a175fea215bb51c4452bb0512e54d159f6485c26fd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclusions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repo")
    def repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repo"))

    @repo.setter
    def repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1807f614ac0a9a8f7d981473a8168781c90326a814e7be040e026d831ce20988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35bac5dbcc653e6fa53148f36a9e4fa33d061b2b4fd068f03b854e49930fbe87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecLibraryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3174428114b345f0f8bf8f5e84dfd2787a3919d00ecd1bfb73f3b19b2e587726)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCran")
    def put_cran(
        self,
        *,
        package: builtins.str,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param package: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        value = DataDatabricksClusterClusterInfoSpecLibraryCran(
            package=package, repo=repo
        )

        return typing.cast(None, jsii.invoke(self, "putCran", [value]))

    @jsii.member(jsii_name="putMaven")
    def put_maven(
        self,
        *,
        coordinates: builtins.str,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param coordinates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#coordinates DataDatabricksCluster#coordinates}.
        :param exclusions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#exclusions DataDatabricksCluster#exclusions}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        value = DataDatabricksClusterClusterInfoSpecLibraryMaven(
            coordinates=coordinates, exclusions=exclusions, repo=repo
        )

        return typing.cast(None, jsii.invoke(self, "putMaven", [value]))

    @jsii.member(jsii_name="putPypi")
    def put_pypi(
        self,
        *,
        package: builtins.str,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param package: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        value = DataDatabricksClusterClusterInfoSpecLibraryPypi(
            package=package, repo=repo
        )

        return typing.cast(None, jsii.invoke(self, "putPypi", [value]))

    @jsii.member(jsii_name="resetCran")
    def reset_cran(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCran", []))

    @jsii.member(jsii_name="resetEgg")
    def reset_egg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgg", []))

    @jsii.member(jsii_name="resetJar")
    def reset_jar(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJar", []))

    @jsii.member(jsii_name="resetMaven")
    def reset_maven(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaven", []))

    @jsii.member(jsii_name="resetPypi")
    def reset_pypi(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPypi", []))

    @jsii.member(jsii_name="resetRequirements")
    def reset_requirements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequirements", []))

    @jsii.member(jsii_name="resetWhl")
    def reset_whl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhl", []))

    @builtins.property
    @jsii.member(jsii_name="cran")
    def cran(self) -> DataDatabricksClusterClusterInfoSpecLibraryCranOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecLibraryCranOutputReference, jsii.get(self, "cran"))

    @builtins.property
    @jsii.member(jsii_name="maven")
    def maven(self) -> DataDatabricksClusterClusterInfoSpecLibraryMavenOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecLibraryMavenOutputReference, jsii.get(self, "maven"))

    @builtins.property
    @jsii.member(jsii_name="pypi")
    def pypi(self) -> "DataDatabricksClusterClusterInfoSpecLibraryPypiOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecLibraryPypiOutputReference", jsii.get(self, "pypi"))

    @builtins.property
    @jsii.member(jsii_name="cranInput")
    def cran_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran], jsii.get(self, "cranInput"))

    @builtins.property
    @jsii.member(jsii_name="eggInput")
    def egg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eggInput"))

    @builtins.property
    @jsii.member(jsii_name="jarInput")
    def jar_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jarInput"))

    @builtins.property
    @jsii.member(jsii_name="mavenInput")
    def maven_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven], jsii.get(self, "mavenInput"))

    @builtins.property
    @jsii.member(jsii_name="pypiInput")
    def pypi_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryPypi"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecLibraryPypi"], jsii.get(self, "pypiInput"))

    @builtins.property
    @jsii.member(jsii_name="requirementsInput")
    def requirements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requirementsInput"))

    @builtins.property
    @jsii.member(jsii_name="whlInput")
    def whl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whlInput"))

    @builtins.property
    @jsii.member(jsii_name="egg")
    def egg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "egg"))

    @egg.setter
    def egg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f5f189143af44cad333144b8f39fc0f8a27aa64dc4c26df982f72f69285649e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egg", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jar")
    def jar(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jar"))

    @jar.setter
    def jar(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7cafcaac178bb838518f290bb9354ff09885cc9807c59e43430cac98767cd63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jar", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requirements")
    def requirements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requirements"))

    @requirements.setter
    def requirements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8652c5d96b7dab43808e4789dc0104ab2269092bb8ed5bea0f35c8f5cb3a87a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requirements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whl")
    def whl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "whl"))

    @whl.setter
    def whl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14fae7f2d4ed1d1c0803e94cd3319918a0c382d6b08efb1ab00040ff6980680f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecLibrary]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecLibrary]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecLibrary]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9119f634533d10816a814225f1a387a233d97892a663994cdfb8ce821faeed4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryPypi",
    jsii_struct_bases=[],
    name_mapping={"package": "package", "repo": "repo"},
)
class DataDatabricksClusterClusterInfoSpecLibraryPypi:
    def __init__(
        self,
        *,
        package: builtins.str,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param package: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dc47a8e625dbe20736e701bfe4557410c19e0d957567c48d2d29855e0b676d5)
            check_type(argname="argument package", value=package, expected_type=type_hints["package"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "package": package,
        }
        if repo is not None:
            self._values["repo"] = repo

    @builtins.property
    def package(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#package DataDatabricksCluster#package}.'''
        result = self._values.get("package")
        assert result is not None, "Required property 'package' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#repo DataDatabricksCluster#repo}.'''
        result = self._values.get("repo")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecLibraryPypi(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecLibraryPypiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecLibraryPypiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d68b51b14bed25db7e22bb7e8c80923c96d3bd086f0e68cdc761a84049b91074)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRepo")
    def reset_repo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepo", []))

    @builtins.property
    @jsii.member(jsii_name="packageInput")
    def package_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "packageInput"))

    @builtins.property
    @jsii.member(jsii_name="repoInput")
    def repo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoInput"))

    @builtins.property
    @jsii.member(jsii_name="package")
    def package(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "package"))

    @package.setter
    def package(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e945f4ec9251a94dbc83c1b496928e328bba50aec59f8c7e1ac7b13907537fca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "package", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repo")
    def repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repo"))

    @repo.setter
    def repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8f3b2ce6715ed1dbae49327364c5619b08cd9b2f877d1b7c6ea0e76d5f1d39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryPypi]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryPypi], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryPypi],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157e7c168f2d5218c438a2e6ee49cf0ae3a4ca5a599154981be31803465934ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19bfd825a33b3d883f5245506fc983ffd68b33ed09e572e3d239b2ebf432ed8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoscale")
    def put_autoscale(
        self,
        *,
        max_workers: typing.Optional[jsii.Number] = None,
        min_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#max_workers DataDatabricksCluster#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#min_workers DataDatabricksCluster#min_workers}.
        '''
        value = DataDatabricksClusterClusterInfoSpecAutoscale(
            max_workers=max_workers, min_workers=min_workers
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscale", [value]))

    @jsii.member(jsii_name="putAwsAttributes")
    def put_aws_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_count DataDatabricksCluster#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_iops DataDatabricksCluster#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_size DataDatabricksCluster#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_throughput DataDatabricksCluster#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#ebs_volume_type DataDatabricksCluster#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#instance_profile_arn DataDatabricksCluster#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_price_percent DataDatabricksCluster#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        value = DataDatabricksClusterClusterInfoSpecAwsAttributes(
            availability=availability,
            ebs_volume_count=ebs_volume_count,
            ebs_volume_iops=ebs_volume_iops,
            ebs_volume_size=ebs_volume_size,
            ebs_volume_throughput=ebs_volume_throughput,
            ebs_volume_type=ebs_volume_type,
            first_on_demand=first_on_demand,
            instance_profile_arn=instance_profile_arn,
            spot_bid_price_percent=spot_bid_price_percent,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAwsAttributes", [value]))

    @jsii.member(jsii_name="putAzureAttributes")
    def put_azure_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#log_analytics_info DataDatabricksCluster#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#spot_bid_max_price DataDatabricksCluster#spot_bid_max_price}.
        '''
        value = DataDatabricksClusterClusterInfoSpecAzureAttributes(
            availability=availability,
            first_on_demand=first_on_demand,
            log_analytics_info=log_analytics_info,
            spot_bid_max_price=spot_bid_max_price,
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAttributes", [value]))

    @jsii.member(jsii_name="putClusterLogConf")
    def put_cluster_log_conf(
        self,
        *,
        dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#dbfs DataDatabricksCluster#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#s3 DataDatabricksCluster#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#volumes DataDatabricksCluster#volumes}
        '''
        value = DataDatabricksClusterClusterInfoSpecClusterLogConf(
            dbfs=dbfs, s3=s3, volumes=volumes
        )

        return typing.cast(None, jsii.invoke(self, "putClusterLogConf", [value]))

    @jsii.member(jsii_name="putClusterMountInfo")
    def put_cluster_mount_info(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecClusterMountInfo, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a04837162fce5341fc2abaf18e96ecfb314391f154fff98ef037ae928b0d781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putClusterMountInfo", [value]))

    @jsii.member(jsii_name="putDockerImage")
    def put_docker_image(
        self,
        *,
        url: builtins.str,
        basic_auth: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#url DataDatabricksCluster#url}.
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#basic_auth DataDatabricksCluster#basic_auth}
        '''
        value = DataDatabricksClusterClusterInfoSpecDockerImage(
            url=url, basic_auth=basic_auth
        )

        return typing.cast(None, jsii.invoke(self, "putDockerImage", [value]))

    @jsii.member(jsii_name="putGcpAttributes")
    def put_gcp_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        boot_disk_size: typing.Optional[jsii.Number] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#availability DataDatabricksCluster#availability}.
        :param boot_disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#boot_disk_size DataDatabricksCluster#boot_disk_size}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#first_on_demand DataDatabricksCluster#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#google_service_account DataDatabricksCluster#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#local_ssd_count DataDatabricksCluster#local_ssd_count}.
        :param use_preemptible_executors: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#use_preemptible_executors DataDatabricksCluster#use_preemptible_executors}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#zone_id DataDatabricksCluster#zone_id}.
        '''
        value = DataDatabricksClusterClusterInfoSpecGcpAttributes(
            availability=availability,
            boot_disk_size=boot_disk_size,
            first_on_demand=first_on_demand,
            google_service_account=google_service_account,
            local_ssd_count=local_ssd_count,
            use_preemptible_executors=use_preemptible_executors,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpAttributes", [value]))

    @jsii.member(jsii_name="putInitScripts")
    def put_init_scripts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecInitScripts, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e137467d74213ca9021bd84cf8197be9ff6b40f180ab432479b58e1e829bd3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInitScripts", [value]))

    @jsii.member(jsii_name="putLibrary")
    def put_library(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecLibrary, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d85a66a5191937dd9bcb97be1c142244e7d853b0397d310a0970f187f32a1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLibrary", [value]))

    @jsii.member(jsii_name="putWorkloadType")
    def put_workload_type(
        self,
        *,
        clients: typing.Union["DataDatabricksClusterClusterInfoSpecWorkloadTypeClients", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param clients: clients block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        value = DataDatabricksClusterClusterInfoSpecWorkloadType(clients=clients)

        return typing.cast(None, jsii.invoke(self, "putWorkloadType", [value]))

    @jsii.member(jsii_name="resetApplyPolicyDefaultValues")
    def reset_apply_policy_default_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyPolicyDefaultValues", []))

    @jsii.member(jsii_name="resetAutoscale")
    def reset_autoscale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscale", []))

    @jsii.member(jsii_name="resetAwsAttributes")
    def reset_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAttributes", []))

    @jsii.member(jsii_name="resetAzureAttributes")
    def reset_azure_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAttributes", []))

    @jsii.member(jsii_name="resetClusterLogConf")
    def reset_cluster_log_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterLogConf", []))

    @jsii.member(jsii_name="resetClusterMountInfo")
    def reset_cluster_mount_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMountInfo", []))

    @jsii.member(jsii_name="resetClusterName")
    def reset_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterName", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDataSecurityMode")
    def reset_data_security_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSecurityMode", []))

    @jsii.member(jsii_name="resetDockerImage")
    def reset_docker_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerImage", []))

    @jsii.member(jsii_name="resetDriverInstancePoolId")
    def reset_driver_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverInstancePoolId", []))

    @jsii.member(jsii_name="resetDriverNodeTypeId")
    def reset_driver_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverNodeTypeId", []))

    @jsii.member(jsii_name="resetEnableElasticDisk")
    def reset_enable_elastic_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableElasticDisk", []))

    @jsii.member(jsii_name="resetEnableLocalDiskEncryption")
    def reset_enable_local_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLocalDiskEncryption", []))

    @jsii.member(jsii_name="resetGcpAttributes")
    def reset_gcp_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAttributes", []))

    @jsii.member(jsii_name="resetIdempotencyToken")
    def reset_idempotency_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdempotencyToken", []))

    @jsii.member(jsii_name="resetInitScripts")
    def reset_init_scripts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitScripts", []))

    @jsii.member(jsii_name="resetInstancePoolId")
    def reset_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolId", []))

    @jsii.member(jsii_name="resetIsSingleNode")
    def reset_is_single_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSingleNode", []))

    @jsii.member(jsii_name="resetKind")
    def reset_kind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKind", []))

    @jsii.member(jsii_name="resetLibrary")
    def reset_library(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLibrary", []))

    @jsii.member(jsii_name="resetNodeTypeId")
    def reset_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeTypeId", []))

    @jsii.member(jsii_name="resetNumWorkers")
    def reset_num_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumWorkers", []))

    @jsii.member(jsii_name="resetPolicyId")
    def reset_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyId", []))

    @jsii.member(jsii_name="resetRemoteDiskThroughput")
    def reset_remote_disk_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteDiskThroughput", []))

    @jsii.member(jsii_name="resetRuntimeEngine")
    def reset_runtime_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuntimeEngine", []))

    @jsii.member(jsii_name="resetSingleUserName")
    def reset_single_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSingleUserName", []))

    @jsii.member(jsii_name="resetSparkConf")
    def reset_spark_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkConf", []))

    @jsii.member(jsii_name="resetSparkEnvVars")
    def reset_spark_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkEnvVars", []))

    @jsii.member(jsii_name="resetSparkVersion")
    def reset_spark_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkVersion", []))

    @jsii.member(jsii_name="resetSshPublicKeys")
    def reset_ssh_public_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshPublicKeys", []))

    @jsii.member(jsii_name="resetTotalInitialRemoteDiskSize")
    def reset_total_initial_remote_disk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalInitialRemoteDiskSize", []))

    @jsii.member(jsii_name="resetUseMlRuntime")
    def reset_use_ml_runtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseMlRuntime", []))

    @jsii.member(jsii_name="resetWorkloadType")
    def reset_workload_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadType", []))

    @builtins.property
    @jsii.member(jsii_name="autoscale")
    def autoscale(self) -> DataDatabricksClusterClusterInfoSpecAutoscaleOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecAutoscaleOutputReference, jsii.get(self, "autoscale"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributes")
    def aws_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecAwsAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecAwsAttributesOutputReference, jsii.get(self, "awsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributes")
    def azure_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecAzureAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecAzureAttributesOutputReference, jsii.get(self, "azureAttributes"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConf")
    def cluster_log_conf(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecClusterLogConfOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecClusterLogConfOutputReference, jsii.get(self, "clusterLogConf"))

    @builtins.property
    @jsii.member(jsii_name="clusterMountInfo")
    def cluster_mount_info(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecClusterMountInfoList:
        return typing.cast(DataDatabricksClusterClusterInfoSpecClusterMountInfoList, jsii.get(self, "clusterMountInfo"))

    @builtins.property
    @jsii.member(jsii_name="dockerImage")
    def docker_image(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecDockerImageOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecDockerImageOutputReference, jsii.get(self, "dockerImage"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributes")
    def gcp_attributes(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecGcpAttributesOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecGcpAttributesOutputReference, jsii.get(self, "gcpAttributes"))

    @builtins.property
    @jsii.member(jsii_name="initScripts")
    def init_scripts(self) -> DataDatabricksClusterClusterInfoSpecInitScriptsList:
        return typing.cast(DataDatabricksClusterClusterInfoSpecInitScriptsList, jsii.get(self, "initScripts"))

    @builtins.property
    @jsii.member(jsii_name="library")
    def library(self) -> DataDatabricksClusterClusterInfoSpecLibraryList:
        return typing.cast(DataDatabricksClusterClusterInfoSpecLibraryList, jsii.get(self, "library"))

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(
        self,
    ) -> "DataDatabricksClusterClusterInfoSpecWorkloadTypeOutputReference":
        return typing.cast("DataDatabricksClusterClusterInfoSpecWorkloadTypeOutputReference", jsii.get(self, "workloadType"))

    @builtins.property
    @jsii.member(jsii_name="applyPolicyDefaultValuesInput")
    def apply_policy_default_values_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "applyPolicyDefaultValuesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleInput")
    def autoscale_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale], jsii.get(self, "autoscaleInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributesInput")
    def aws_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes], jsii.get(self, "awsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributesInput")
    def azure_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes], jsii.get(self, "azureAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConfInput")
    def cluster_log_conf_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf], jsii.get(self, "clusterLogConfInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterMountInfoInput")
    def cluster_mount_info_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]], jsii.get(self, "clusterMountInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSecurityModeInput")
    def data_security_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="dockerImageInput")
    def docker_image_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage], jsii.get(self, "dockerImageInput"))

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolIdInput")
    def driver_instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInstancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeIdInput")
    def driver_node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverNodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enableElasticDiskInput")
    def enable_elastic_disk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableElasticDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryptionInput")
    def enable_local_disk_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableLocalDiskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributesInput")
    def gcp_attributes_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes], jsii.get(self, "gcpAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="idempotencyTokenInput")
    def idempotency_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idempotencyTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="initScriptsInput")
    def init_scripts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]], jsii.get(self, "initScriptsInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolIdInput")
    def instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="isSingleNodeInput")
    def is_single_node_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSingleNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property
    @jsii.member(jsii_name="libraryInput")
    def library_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]], jsii.get(self, "libraryInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeIdInput")
    def node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="numWorkersInput")
    def num_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteDiskThroughputInput")
    def remote_disk_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "remoteDiskThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="runtimeEngineInput")
    def runtime_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeEngineInput"))

    @builtins.property
    @jsii.member(jsii_name="singleUserNameInput")
    def single_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "singleUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkConfInput")
    def spark_conf_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkConfInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVarsInput")
    def spark_env_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkEnvVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkVersionInput")
    def spark_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sparkVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeysInput")
    def ssh_public_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshPublicKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="totalInitialRemoteDiskSizeInput")
    def total_initial_remote_disk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalInitialRemoteDiskSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="useMlRuntimeInput")
    def use_ml_runtime_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useMlRuntimeInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(
        self,
    ) -> typing.Optional["DataDatabricksClusterClusterInfoSpecWorkloadType"]:
        return typing.cast(typing.Optional["DataDatabricksClusterClusterInfoSpecWorkloadType"], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="applyPolicyDefaultValues")
    def apply_policy_default_values(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "applyPolicyDefaultValues"))

    @apply_policy_default_values.setter
    def apply_policy_default_values(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5afbcc3c25f6ce4c96e8e167be30b9797f35232a06111a821a1efa010c788b4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applyPolicyDefaultValues", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2e5db786428fa3fee61394268fd49f8815387e375284a99c5c9980210c45e4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e33700fa94ba9a8101dea5fb5bb9135f6452c680dcb8fc0a7b76301d724b242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSecurityMode")
    def data_security_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSecurityMode"))

    @data_security_mode.setter
    def data_security_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba951d6a9111c09ccb8363b71e621e123cd72a50489de01e16ac5062b4cc464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSecurityMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolId")
    def driver_instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverInstancePoolId"))

    @driver_instance_pool_id.setter
    def driver_instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3d337f8e443f8f0ad575439badf32ee62c4c6fb649503638b1ddc58e6cda4cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverInstancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeId")
    def driver_node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverNodeTypeId"))

    @driver_node_type_id.setter
    def driver_node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f7b61ee021c6391b020506b58c50aebce87c7922c9e9be5f0cab139945f8b46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverNodeTypeId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__81b29bd380315668bc65fa9448e1c0b5da73c1036f99175ac9638fc8572c5595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableElasticDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryption")
    def enable_local_disk_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableLocalDiskEncryption"))

    @enable_local_disk_encryption.setter
    def enable_local_disk_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d455d711ef049633c2f9955e8d8e4eb21970102cd27421776e52c8a159ecbb0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableLocalDiskEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idempotencyToken")
    def idempotency_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idempotencyToken"))

    @idempotency_token.setter
    def idempotency_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d0d9f807fc111dc623705ab471fa638879f6baeb2ef26a4247290d42cb5fac1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idempotencyToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d434a16819a9d2bccde8c726679c0894180cba9f556778e8820dd9db681fef13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSingleNode")
    def is_single_node(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSingleNode"))

    @is_single_node.setter
    def is_single_node(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c44d9bc7690e324527952379db56f52f429aebfd7bd51dc617d0df03f084555)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSingleNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__311b1e73eda77b31f3c4836e1cccacf70e35693b81bc8d56a3294feaa1db0903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edd99694443de18f9e011708fe5b5c2133f0e00a8adf97a69ebc1e8b80af5068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numWorkers")
    def num_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numWorkers"))

    @num_workers.setter
    def num_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c470e5ec4ddd3e13565296c1ee8b0f2512fd18dcd543f8f9b5ab004d5fddb24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c736425080bca43855f5a70bb10c62c6f4f315d1db46495a82b638d937e03b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteDiskThroughput")
    def remote_disk_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "remoteDiskThroughput"))

    @remote_disk_throughput.setter
    def remote_disk_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8caffcccb3069bb30778444e07cf07e287903be711e4a82562d24a81e79928bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteDiskThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runtimeEngine")
    def runtime_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtimeEngine"))

    @runtime_engine.setter
    def runtime_engine(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94c13f5eff29c15ca06b42838c97a8156cb8ac591ab243c1fdb0137cff1983d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runtimeEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="singleUserName")
    def single_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "singleUserName"))

    @single_user_name.setter
    def single_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eeac916fa9c5218d0e4e2e4afdb55aedfe7552dae447f2b2911f184b16b0925)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "singleUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkConf")
    def spark_conf(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkConf"))

    @spark_conf.setter
    def spark_conf(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__153fee277bd2f384cee55621fa220dee274ef71e37754085075214c6de91eed5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkConf", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVars")
    def spark_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkEnvVars"))

    @spark_env_vars.setter
    def spark_env_vars(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa3e3092ae2a5fcab6a3c40bda6e67bc31aa334e6c4ca58eeb7f881e8b962c0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkEnvVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkVersion")
    def spark_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sparkVersion"))

    @spark_version.setter
    def spark_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a28b808459d9ed2d2076d11df58347c51076164987c76cc0ff5a1fe05a09c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeys")
    def ssh_public_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshPublicKeys"))

    @ssh_public_keys.setter
    def ssh_public_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__045f1ba64894523c52e80aeed7184bf0bdfc192e22ed850a6abf21c3b8487ebd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshPublicKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalInitialRemoteDiskSize")
    def total_initial_remote_disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalInitialRemoteDiskSize"))

    @total_initial_remote_disk_size.setter
    def total_initial_remote_disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31be5e42b41a7a14eeed51bba7642f502ee931ff49ec4a069667bca5addbab5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalInitialRemoteDiskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useMlRuntime")
    def use_ml_runtime(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useMlRuntime"))

    @use_ml_runtime.setter
    def use_ml_runtime(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1d585f8c279d923e30538939c53bb7938f46881ab651d2604c2142f65ae3f53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useMlRuntime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksClusterClusterInfoSpec]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__249bcb59dbbdb1492604acd69a1a0c3433d865b30409d6f7db6eb5016b728a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecWorkloadType",
    jsii_struct_bases=[],
    name_mapping={"clients": "clients"},
)
class DataDatabricksClusterClusterInfoSpecWorkloadType:
    def __init__(
        self,
        *,
        clients: typing.Union["DataDatabricksClusterClusterInfoSpecWorkloadTypeClients", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param clients: clients block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        if isinstance(clients, dict):
            clients = DataDatabricksClusterClusterInfoSpecWorkloadTypeClients(**clients)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__829609e77b5ab569a3822505894f51c66588de7c73a865a1f209a1c75f0a4ef1)
            check_type(argname="argument clients", value=clients, expected_type=type_hints["clients"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "clients": clients,
        }

    @builtins.property
    def clients(self) -> "DataDatabricksClusterClusterInfoSpecWorkloadTypeClients":
        '''clients block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        result = self._values.get("clients")
        assert result is not None, "Required property 'clients' is missing"
        return typing.cast("DataDatabricksClusterClusterInfoSpecWorkloadTypeClients", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecWorkloadType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecWorkloadTypeClients",
    jsii_struct_bases=[],
    name_mapping={"jobs": "jobs", "notebooks": "notebooks"},
)
class DataDatabricksClusterClusterInfoSpecWorkloadTypeClients:
    def __init__(
        self,
        *,
        jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jobs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.
        :param notebooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4b1e0ede642cc6c3ad2286ff3172c31e0be9b0d8a07bb24a8b50a00d9ad1b29)
            check_type(argname="argument jobs", value=jobs, expected_type=type_hints["jobs"])
            check_type(argname="argument notebooks", value=notebooks, expected_type=type_hints["notebooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if jobs is not None:
            self._values["jobs"] = jobs
        if notebooks is not None:
            self._values["notebooks"] = notebooks

    @builtins.property
    def jobs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.'''
        result = self._values.get("jobs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def notebooks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.'''
        result = self._values.get("notebooks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoSpecWorkloadTypeClients(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoSpecWorkloadTypeClientsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecWorkloadTypeClientsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d663bf8125b4b36a12685e0ebcff7b379a095806b9a24cfd73cd464079d85dac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetJobs")
    def reset_jobs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobs", []))

    @jsii.member(jsii_name="resetNotebooks")
    def reset_notebooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebooks", []))

    @builtins.property
    @jsii.member(jsii_name="jobsInput")
    def jobs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jobsInput"))

    @builtins.property
    @jsii.member(jsii_name="notebooksInput")
    def notebooks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notebooksInput"))

    @builtins.property
    @jsii.member(jsii_name="jobs")
    def jobs(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jobs"))

    @jobs.setter
    def jobs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c0ac3dac402b289a47da0e6979866ac49c00c717ac4ff2d2dc1d9142187bded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notebooks")
    def notebooks(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notebooks"))

    @notebooks.setter
    def notebooks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__769be5f4897eb16ead30a07eace8cd1f19d2b95b09bb8e7c4dd022d8382ebc1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebooks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4679170011a43ab31dc3b1627ecc549de9df5ec18b60699f8c51607b867e3d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoSpecWorkloadTypeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoSpecWorkloadTypeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d23b94310b9420193325214a9412b09624c00bd87792a90e9be7c703ef961253)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putClients")
    def put_clients(
        self,
        *,
        jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jobs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.
        :param notebooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.
        '''
        value = DataDatabricksClusterClusterInfoSpecWorkloadTypeClients(
            jobs=jobs, notebooks=notebooks
        )

        return typing.cast(None, jsii.invoke(self, "putClients", [value]))

    @builtins.property
    @jsii.member(jsii_name="clients")
    def clients(
        self,
    ) -> DataDatabricksClusterClusterInfoSpecWorkloadTypeClientsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoSpecWorkloadTypeClientsOutputReference, jsii.get(self, "clients"))

    @builtins.property
    @jsii.member(jsii_name="clientsInput")
    def clients_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients], jsii.get(self, "clientsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadType]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadType], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadType],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be78376369f4796e732092b677594d6e47d89aabe0e0e070fa1c95fbf247d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoTerminationReason",
    jsii_struct_bases=[],
    name_mapping={"code": "code", "parameters": "parameters", "type": "type"},
)
class DataDatabricksClusterClusterInfoTerminationReason:
    def __init__(
        self,
        *,
        code: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#code DataDatabricksCluster#code}.
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#parameters DataDatabricksCluster#parameters}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#type DataDatabricksCluster#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd5c85764d53a6a4757976c6afb6b9b08b261d72a2016989577d23d61465207e)
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if code is not None:
            self._values["code"] = code
        if parameters is not None:
            self._values["parameters"] = parameters
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#code DataDatabricksCluster#code}.'''
        result = self._values.get("code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#parameters DataDatabricksCluster#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#type DataDatabricksCluster#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoTerminationReason(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoTerminationReasonOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoTerminationReasonOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__667dbbc3761b52f06c124e18c7baf96ce16c2927ba83bbf2f18ac82ce2033df5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCode")
    def reset_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCode", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="codeInput")
    def code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "codeInput"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="code")
    def code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "code"))

    @code.setter
    def code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d6facbb0e5042ca7ebb6859f6f9f9e9cb000005629a953b771383a3b2822d17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "code", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba9947e8c0a19dda024e1fee231e0704c4555511b63c76f04ae5a5733c60eee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__289d4bcfa3e10257d339406f9dbefb519145b6d376e481896452de7811e0ff21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoTerminationReason]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoTerminationReason], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoTerminationReason],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccc5ff823ef83a3ee59591beae4019de81097d91ce6fa8f75b8a9f2eba9ddc04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoWorkloadType",
    jsii_struct_bases=[],
    name_mapping={"clients": "clients"},
)
class DataDatabricksClusterClusterInfoWorkloadType:
    def __init__(
        self,
        *,
        clients: typing.Union["DataDatabricksClusterClusterInfoWorkloadTypeClients", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param clients: clients block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        if isinstance(clients, dict):
            clients = DataDatabricksClusterClusterInfoWorkloadTypeClients(**clients)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c52abaf00517d61ef032c48f79dc6da854a6fbca384b8ca84c798086f62ae2)
            check_type(argname="argument clients", value=clients, expected_type=type_hints["clients"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "clients": clients,
        }

    @builtins.property
    def clients(self) -> "DataDatabricksClusterClusterInfoWorkloadTypeClients":
        '''clients block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#clients DataDatabricksCluster#clients}
        '''
        result = self._values.get("clients")
        assert result is not None, "Required property 'clients' is missing"
        return typing.cast("DataDatabricksClusterClusterInfoWorkloadTypeClients", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoWorkloadType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoWorkloadTypeClients",
    jsii_struct_bases=[],
    name_mapping={"jobs": "jobs", "notebooks": "notebooks"},
)
class DataDatabricksClusterClusterInfoWorkloadTypeClients:
    def __init__(
        self,
        *,
        jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jobs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.
        :param notebooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa910f7f39cfc7a8d092dcdf175efc21db164c0c8e89ef204576960bb17051e)
            check_type(argname="argument jobs", value=jobs, expected_type=type_hints["jobs"])
            check_type(argname="argument notebooks", value=notebooks, expected_type=type_hints["notebooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if jobs is not None:
            self._values["jobs"] = jobs
        if notebooks is not None:
            self._values["notebooks"] = notebooks

    @builtins.property
    def jobs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.'''
        result = self._values.get("jobs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def notebooks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.'''
        result = self._values.get("notebooks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksClusterClusterInfoWorkloadTypeClients(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksClusterClusterInfoWorkloadTypeClientsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoWorkloadTypeClientsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2eedbbdbcd36898ffda5a0192f44d059651e5e49a9e41a14c1b0dd597105887)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetJobs")
    def reset_jobs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobs", []))

    @jsii.member(jsii_name="resetNotebooks")
    def reset_notebooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebooks", []))

    @builtins.property
    @jsii.member(jsii_name="jobsInput")
    def jobs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jobsInput"))

    @builtins.property
    @jsii.member(jsii_name="notebooksInput")
    def notebooks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notebooksInput"))

    @builtins.property
    @jsii.member(jsii_name="jobs")
    def jobs(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jobs"))

    @jobs.setter
    def jobs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b65b820b13a2a14bf4592dd7c133176be553203f4a75afca82d41157c99e03bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notebooks")
    def notebooks(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notebooks"))

    @notebooks.setter
    def notebooks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a39c8e5a10a63a592b1f27b73f03556d67e642bffec8e60946e8d1f0665d8177)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebooks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__878b69da8140018a03bc4b928ee6776b510c28002cef346ef2c5904de310a405)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksClusterClusterInfoWorkloadTypeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterClusterInfoWorkloadTypeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f776185001279ec713db13590cb93b4ed3114f6202e6d0d6289027c494dabeaa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putClients")
    def put_clients(
        self,
        *,
        jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jobs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#jobs DataDatabricksCluster#jobs}.
        :param notebooks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#notebooks DataDatabricksCluster#notebooks}.
        '''
        value = DataDatabricksClusterClusterInfoWorkloadTypeClients(
            jobs=jobs, notebooks=notebooks
        )

        return typing.cast(None, jsii.invoke(self, "putClients", [value]))

    @builtins.property
    @jsii.member(jsii_name="clients")
    def clients(
        self,
    ) -> DataDatabricksClusterClusterInfoWorkloadTypeClientsOutputReference:
        return typing.cast(DataDatabricksClusterClusterInfoWorkloadTypeClientsOutputReference, jsii.get(self, "clients"))

    @builtins.property
    @jsii.member(jsii_name="clientsInput")
    def clients_input(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients], jsii.get(self, "clientsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksClusterClusterInfoWorkloadType]:
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfoWorkloadType], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksClusterClusterInfoWorkloadType],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca10044f44f0d9fccb7e88992e90a2347f94ade9afb643a011594494d3f82194)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksCluster.DataDatabricksClusterConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_id": "clusterId",
        "cluster_info": "clusterInfo",
        "cluster_name": "clusterName",
        "id": "id",
    },
)
class DataDatabricksClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
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
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.
        :param cluster_info: cluster_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_info DataDatabricksCluster#cluster_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#id DataDatabricksCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cluster_info, dict):
            cluster_info = DataDatabricksClusterClusterInfo(**cluster_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24360d74477cd67ee067f91407d4d0a33d77c869b9801fe22eca42b827f2e79)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument cluster_info", value=cluster_info, expected_type=type_hints["cluster_info"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
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
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if cluster_info is not None:
            self._values["cluster_info"] = cluster_info
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
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
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_id DataDatabricksCluster#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_info(self) -> typing.Optional[DataDatabricksClusterClusterInfo]:
        '''cluster_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_info DataDatabricksCluster#cluster_info}
        '''
        result = self._values.get("cluster_info")
        return typing.cast(typing.Optional[DataDatabricksClusterClusterInfo], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#cluster_name DataDatabricksCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/cluster#id DataDatabricksCluster#id}.

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
        return "DataDatabricksClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksCluster",
    "DataDatabricksClusterClusterInfo",
    "DataDatabricksClusterClusterInfoAutoscale",
    "DataDatabricksClusterClusterInfoAutoscaleOutputReference",
    "DataDatabricksClusterClusterInfoAwsAttributes",
    "DataDatabricksClusterClusterInfoAwsAttributesOutputReference",
    "DataDatabricksClusterClusterInfoAzureAttributes",
    "DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo",
    "DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfoOutputReference",
    "DataDatabricksClusterClusterInfoAzureAttributesOutputReference",
    "DataDatabricksClusterClusterInfoClusterLogConf",
    "DataDatabricksClusterClusterInfoClusterLogConfDbfs",
    "DataDatabricksClusterClusterInfoClusterLogConfDbfsOutputReference",
    "DataDatabricksClusterClusterInfoClusterLogConfOutputReference",
    "DataDatabricksClusterClusterInfoClusterLogConfS3",
    "DataDatabricksClusterClusterInfoClusterLogConfS3OutputReference",
    "DataDatabricksClusterClusterInfoClusterLogConfVolumes",
    "DataDatabricksClusterClusterInfoClusterLogConfVolumesOutputReference",
    "DataDatabricksClusterClusterInfoClusterLogStatus",
    "DataDatabricksClusterClusterInfoClusterLogStatusOutputReference",
    "DataDatabricksClusterClusterInfoDockerImage",
    "DataDatabricksClusterClusterInfoDockerImageBasicAuth",
    "DataDatabricksClusterClusterInfoDockerImageBasicAuthOutputReference",
    "DataDatabricksClusterClusterInfoDockerImageOutputReference",
    "DataDatabricksClusterClusterInfoDriver",
    "DataDatabricksClusterClusterInfoDriverNodeAwsAttributes",
    "DataDatabricksClusterClusterInfoDriverNodeAwsAttributesOutputReference",
    "DataDatabricksClusterClusterInfoDriverOutputReference",
    "DataDatabricksClusterClusterInfoExecutors",
    "DataDatabricksClusterClusterInfoExecutorsList",
    "DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes",
    "DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributesOutputReference",
    "DataDatabricksClusterClusterInfoExecutorsOutputReference",
    "DataDatabricksClusterClusterInfoGcpAttributes",
    "DataDatabricksClusterClusterInfoGcpAttributesOutputReference",
    "DataDatabricksClusterClusterInfoInitScripts",
    "DataDatabricksClusterClusterInfoInitScriptsAbfss",
    "DataDatabricksClusterClusterInfoInitScriptsAbfssOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsDbfs",
    "DataDatabricksClusterClusterInfoInitScriptsDbfsOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsFile",
    "DataDatabricksClusterClusterInfoInitScriptsFileOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsGcs",
    "DataDatabricksClusterClusterInfoInitScriptsGcsOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsList",
    "DataDatabricksClusterClusterInfoInitScriptsOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsS3",
    "DataDatabricksClusterClusterInfoInitScriptsS3OutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsVolumes",
    "DataDatabricksClusterClusterInfoInitScriptsVolumesOutputReference",
    "DataDatabricksClusterClusterInfoInitScriptsWorkspace",
    "DataDatabricksClusterClusterInfoInitScriptsWorkspaceOutputReference",
    "DataDatabricksClusterClusterInfoOutputReference",
    "DataDatabricksClusterClusterInfoSpec",
    "DataDatabricksClusterClusterInfoSpecAutoscale",
    "DataDatabricksClusterClusterInfoSpecAutoscaleOutputReference",
    "DataDatabricksClusterClusterInfoSpecAwsAttributes",
    "DataDatabricksClusterClusterInfoSpecAwsAttributesOutputReference",
    "DataDatabricksClusterClusterInfoSpecAzureAttributes",
    "DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo",
    "DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfoOutputReference",
    "DataDatabricksClusterClusterInfoSpecAzureAttributesOutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterLogConf",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfDbfsOutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfOutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfS3",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfS3OutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes",
    "DataDatabricksClusterClusterInfoSpecClusterLogConfVolumesOutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterMountInfo",
    "DataDatabricksClusterClusterInfoSpecClusterMountInfoList",
    "DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo",
    "DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfoOutputReference",
    "DataDatabricksClusterClusterInfoSpecClusterMountInfoOutputReference",
    "DataDatabricksClusterClusterInfoSpecDockerImage",
    "DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth",
    "DataDatabricksClusterClusterInfoSpecDockerImageBasicAuthOutputReference",
    "DataDatabricksClusterClusterInfoSpecDockerImageOutputReference",
    "DataDatabricksClusterClusterInfoSpecGcpAttributes",
    "DataDatabricksClusterClusterInfoSpecGcpAttributesOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScripts",
    "DataDatabricksClusterClusterInfoSpecInitScriptsAbfss",
    "DataDatabricksClusterClusterInfoSpecInitScriptsAbfssOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsDbfs",
    "DataDatabricksClusterClusterInfoSpecInitScriptsDbfsOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsFile",
    "DataDatabricksClusterClusterInfoSpecInitScriptsFileOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsGcs",
    "DataDatabricksClusterClusterInfoSpecInitScriptsGcsOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsList",
    "DataDatabricksClusterClusterInfoSpecInitScriptsOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsS3",
    "DataDatabricksClusterClusterInfoSpecInitScriptsS3OutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsVolumes",
    "DataDatabricksClusterClusterInfoSpecInitScriptsVolumesOutputReference",
    "DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace",
    "DataDatabricksClusterClusterInfoSpecInitScriptsWorkspaceOutputReference",
    "DataDatabricksClusterClusterInfoSpecLibrary",
    "DataDatabricksClusterClusterInfoSpecLibraryCran",
    "DataDatabricksClusterClusterInfoSpecLibraryCranOutputReference",
    "DataDatabricksClusterClusterInfoSpecLibraryList",
    "DataDatabricksClusterClusterInfoSpecLibraryMaven",
    "DataDatabricksClusterClusterInfoSpecLibraryMavenOutputReference",
    "DataDatabricksClusterClusterInfoSpecLibraryOutputReference",
    "DataDatabricksClusterClusterInfoSpecLibraryPypi",
    "DataDatabricksClusterClusterInfoSpecLibraryPypiOutputReference",
    "DataDatabricksClusterClusterInfoSpecOutputReference",
    "DataDatabricksClusterClusterInfoSpecWorkloadType",
    "DataDatabricksClusterClusterInfoSpecWorkloadTypeClients",
    "DataDatabricksClusterClusterInfoSpecWorkloadTypeClientsOutputReference",
    "DataDatabricksClusterClusterInfoSpecWorkloadTypeOutputReference",
    "DataDatabricksClusterClusterInfoTerminationReason",
    "DataDatabricksClusterClusterInfoTerminationReasonOutputReference",
    "DataDatabricksClusterClusterInfoWorkloadType",
    "DataDatabricksClusterClusterInfoWorkloadTypeClients",
    "DataDatabricksClusterClusterInfoWorkloadTypeClientsOutputReference",
    "DataDatabricksClusterClusterInfoWorkloadTypeOutputReference",
    "DataDatabricksClusterConfig",
]

publication.publish()

def _typecheckingstub__d133c2fd37787cfe43f23e1d478942cd52dc142a57aceadf6477ff7c50381355(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: typing.Optional[builtins.str] = None,
    cluster_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0016c77e21b1df6e1dbd79f7fade0623d63c05e92b4695ffd32856bf16c96478(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1699c6d848ec00fbed18a9f53dd4386a43a0c9d2af33c5e47b8803879c8ee32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14b1f6c30036d34c5f75edd72d49dc0dec54c8f6254430e489472f8976ad78c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1e08b76b622e3dd6d91d7dcdba3e2e0e80c418de24692c7e9c4c8027c38699(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aff56b34c6a8acca8a91fda42e2e8676c9973443a5d6dd43eb7430c934f05b0b(
    *,
    autoscale: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoAutoscale, typing.Dict[builtins.str, typing.Any]]] = None,
    autotermination_minutes: typing.Optional[jsii.Number] = None,
    aws_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_cores: typing.Optional[jsii.Number] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    cluster_log_conf: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConf, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_log_status: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogStatus, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_memory_mb: typing.Optional[jsii.Number] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    cluster_source: typing.Optional[builtins.str] = None,
    creator_user_name: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    data_security_mode: typing.Optional[builtins.str] = None,
    default_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    docker_image: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDockerImage, typing.Dict[builtins.str, typing.Any]]] = None,
    driver: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDriver, typing.Dict[builtins.str, typing.Any]]] = None,
    driver_instance_pool_id: typing.Optional[builtins.str] = None,
    driver_node_type_id: typing.Optional[builtins.str] = None,
    enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    executors: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoExecutors, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoInitScripts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    jdbc_port: typing.Optional[jsii.Number] = None,
    kind: typing.Optional[builtins.str] = None,
    last_restarted_time: typing.Optional[jsii.Number] = None,
    last_state_loss_time: typing.Optional[jsii.Number] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    num_workers: typing.Optional[jsii.Number] = None,
    policy_id: typing.Optional[builtins.str] = None,
    remote_disk_throughput: typing.Optional[jsii.Number] = None,
    runtime_engine: typing.Optional[builtins.str] = None,
    single_user_name: typing.Optional[builtins.str] = None,
    spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    spark_context_id: typing.Optional[jsii.Number] = None,
    spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    spark_version: typing.Optional[builtins.str] = None,
    spec: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    start_time: typing.Optional[jsii.Number] = None,
    state: typing.Optional[builtins.str] = None,
    state_message: typing.Optional[builtins.str] = None,
    terminated_time: typing.Optional[jsii.Number] = None,
    termination_reason: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoTerminationReason, typing.Dict[builtins.str, typing.Any]]] = None,
    total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
    use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_type: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoWorkloadType, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e611460c20d10cf5c9c52b420e6d78c49d6eae8b4d26c09982229c9983ffb68d(
    *,
    max_workers: typing.Optional[jsii.Number] = None,
    min_workers: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35752c886237667ffca38ea033402a4e9333b885632e81a2fdba0ea08174af11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14dc64da28b5cfd0c61243c07e441d9d2af1cd1d1b83ad793d43f1e16e1a705a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c1fa899208a7be3f7baf39c8f39d706c6d8e94b1397c6a09e4a8fe3f8c74f3c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__337c2d0342fca3dddf815ca98a3797af7bc5fad84fff22adb1d9d9db6e116476(
    value: typing.Optional[DataDatabricksClusterClusterInfoAutoscale],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__060687017a6683f4c7f78822b15c7edf71b45e792e6249e9114a0bd28c23aa44(
    *,
    availability: typing.Optional[builtins.str] = None,
    ebs_volume_count: typing.Optional[jsii.Number] = None,
    ebs_volume_iops: typing.Optional[jsii.Number] = None,
    ebs_volume_size: typing.Optional[jsii.Number] = None,
    ebs_volume_throughput: typing.Optional[jsii.Number] = None,
    ebs_volume_type: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    spot_bid_price_percent: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f81ba997844101640d70c2697e7cc6abfa14535428a19fbd5a364455c84ff89c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970f4adf30aee8f77e0e6d817564d02f6641dc9b044f98726f732589738de46c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4323aea0be122647bb06a0285e94de2af7992410275f13bf6796e85eebd915(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eba9f9990fdbb1a179d2285d80453b5a2f416cb705d7bf24b3784bda759d8d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc009aa4886cd3b1ee07a4bb78e804a0c7030fb8ce68e0dbf3193e04ecda199(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba748dc3c78f2e79400a1429570fcbb7a73d24771ac0ed343fe98fe273ff85c3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b6140b00e2942864335c6191127f33cf6b842e08ee35641cbd1763ec98c33e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b796f7ee77bd1bed67214cd1ac7faf229537b451e335ea182249ff6c28bf701f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e850214790cae037d58a4842aca1cea1fb0e6fd882aa56bab20c45c3a32a574c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5882a8b5ec4aee904787873dec8524946e1ef601968589355ad1d033835f5b5c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd2c3108d6f2222e31260a3f70143204c9398825bae67dd37da38f9b2041d683(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd26067baedf055eb6b688c456c4f12e95331dc5caf70f9d03a291927f99fcbd(
    value: typing.Optional[DataDatabricksClusterClusterInfoAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec36542822dccc27e818d16be714f69c4d1671962cbc195c82c6a8c2f4c0898(
    *,
    availability: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    log_analytics_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_bid_max_price: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a2946db0de955bc04b2b2a53da4db21aafdcfa008d2bc69e78d8040c29b29c(
    *,
    log_analytics_primary_key: typing.Optional[builtins.str] = None,
    log_analytics_workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94d2e3dbc3ccd24b9da490b8da4917dcdf843944f3148430d9bf4d851e095205(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce148e5a0f57eeb3a89ef8dede0bff9c564bde5c238af89c48d3f599b00a175(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0835188fbcc4809a7826a8aa136569e75869bf124d5980769a34198e2b765bce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c94723209830e8be1b3e7045f809f349f0f635e7d96142faa90d15dcfa13ba8(
    value: typing.Optional[DataDatabricksClusterClusterInfoAzureAttributesLogAnalyticsInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c8cd141c27b2c2d846117e13a084afe4de0adb973d2c1a1ffae84582aea867(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6424770ffe309b2b0596e3133a285f97f9cc34fb8becf973de311bf538b81b06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__437e341f232c0196c3231119587bd7731d1cd35bb6942685b698b2199678905d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd728ef2f2d7c0aea03746777640d078ca7844dc757c2310a3580c4f35a683f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7384228cb2140c413611389d532bdd60910faa170bf821e2f4510f803dda64c0(
    value: typing.Optional[DataDatabricksClusterClusterInfoAzureAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__451a0c7c98565e47235d6e74d8b7df3a27673c5b4ca678ef26a4fa85f482d840(
    *,
    dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c94e315810d4fa1309fd5dec46d327742f2d4085d58f8cb903a5a494c4ddf37(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07825f2e9284d1ca8e150d5afb12188fbb5125d2fbcc670814e0f62cb24fa46d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__081580da1789e207814624e3b17cfbc036ec41532b1d044cd41ce3e61e55a148(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29310c16851df40418ad05d40fd87fbf755255521e34b4dba84643d3f70cc7e3(
    value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f5bba261ec9a275ca87196a5f385380ba15d0028a7a1aecc19a58850136a59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d81804f6a7c21bfef2b0e11931361538d05ea1c9ed713de3438b51ea675997b(
    value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConf],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20a2a7d01952ab164f7d87d0bdc7769de04513a471d6140efabf33dc3da46064(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06131481b14249278ca738634899d5f1aee5b331e334cfc5c48f8e3b894130bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f00b1c1ed199eead343b576ac29a3e0e8eaace9d3cbcbc2f2eb9166f38b7d88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3109fbd61353ab7c9c73f5e31f36a2a40d764e9d09c42f0bebb71f2e52fe065b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36e56a73067a73d1016168b1f098162c69b3eebeb003c0dc61e346a9e6cab188(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8177e776b121dc504a45757a3336701af5a48e9806c4f483985d3faac7d86bd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__407842af49d6404da7b4553f4126f123d749691f92f2e6c5cb2c03c728eb700f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__869a15040243a0463170f8060ae98b7d6908ec237afb7d1dacaa4f60339a82ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a4977fc0bfa4a03a4a53921b1e36b2c3858028174c02bf48c49897cdb00061e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d86bf06b7f50dda5d2103bf087b9ba2529c4d8a880829f264a968d944dde5f67(
    value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e90624a2c8601efd03da3b11dc645f55f646d9f8bfd246785b305793af1bb6eb(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb22a8ff0ad2cc8dc5b2d255e1f3d64bca2d6bb95a2b1d4e9d852c549bae44c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e32ed85d2b0cc28288d57fd0fb6709ed2a8c594f3ac11ab6a21588ada7f1e163(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c74adcb7f68c12a967d0f454d09b91b2f15d0b7e6ff9adf2d1cbae06c2000aa(
    value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogConfVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06eeb3670b53e443ccf228f492206924ef7cb9d635763a487922dc8c29ab499b(
    *,
    last_attempted: typing.Optional[jsii.Number] = None,
    last_exception: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aadd2ed8a3715c1520c7488e955f04daceb0c20d323f34068ce4ce693f50eaf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583222fcf9d9569f58e7eef639cca9e138348f024b6a611c227c8d97c45c2eb0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b37043262f004f19a42be3f013b4dee4411fbacd9b09a65c78468bd07bdf309b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf21fd1ca134e80581ef285c950289788e8e8ede383ce2ec0583d203711f1a18(
    value: typing.Optional[DataDatabricksClusterClusterInfoClusterLogStatus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dfbaa9d7aa202bcc8a3aa88db3acb8adcf55e3affad038966e42a54f8a3f953(
    *,
    basic_auth: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__761b360360d2ab65569cc14de4c4c9c4f717740017d648342b5e6fb63dd4e09c(
    *,
    password: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b19c8260c8e15473c09850b67e8e8287922bf30d63be715bee653d6540c91492(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32cb61c3b2556c2d374a33a1ecb04e9e757092b3bec8b0bcf2b7c71cadd02155(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c781b02d8b4f5df06440507923978efc3f4724b0afa44b8693fb51a8bdeb7fe3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07eb9eb22b21828dd8f083e769e7963f340d7b1c6d3b2e40d99291297668ba9(
    value: typing.Optional[DataDatabricksClusterClusterInfoDockerImageBasicAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334c4508d85bb7cb0ad8ddaa500f071d805b42cf609576815edcba98247b585f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12f2e2b7c8aa32dbdd3f65ad24a74bd9b07d85e1939f30ada93a03bac74b01ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__928b91e38802299174dfb1a813070bd8711d9f10a88ceac8209ff59f40f46f3a(
    value: typing.Optional[DataDatabricksClusterClusterInfoDockerImage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93d8d212082c22fe59b0dc2b07716ae7e3d544e4b77399dfdcee1f09cb003495(
    *,
    host_private_ip: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    node_aws_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    node_id: typing.Optional[builtins.str] = None,
    private_ip: typing.Optional[builtins.str] = None,
    public_dns: typing.Optional[builtins.str] = None,
    start_timestamp: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09872ab0283a84c409df67e91d2316d1b5d3eaae51d0db90897561ae1a41d24(
    *,
    is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c37ffb02f798d989938f533b51690208d4ab02fe50b00dcbfadfd9b1932af3a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51f1ac2146b5423809e5619e9e85bff0c8a2c572440ba3faefd9bba6b5750520(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024693618d340fd40b6470e408ceda0f1ebe2ec8120a8f028da5dd2857662b36(
    value: typing.Optional[DataDatabricksClusterClusterInfoDriverNodeAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c29e03d20b78011fdf7121f78aae8f82946665c67d44b13c1320a4e9bacb302(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde72e430cb3a61e8e71b9a31745a7526f13eb8d2912794722626b3d3ec45a90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca0440698826da0d2ac51093146016942cd1e3d647091d46c2f89d61218e5e93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32da65206da6c7035041e62f70e14f0a695da880430f9e9d864c4244d6605ec6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3586f5c9abe693664abec246aaba325b24bb402704972844829f16969059e090(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6d900b1919d61519f6ba03d4d6a965fbd45cab554f85179654cd5f60d00e02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7b76ad4f2df6d8f724ab48ff6954a93ce30217e4ddd54e072be81fc43fe600(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__413aa894dd397a7d674d5ac2d68e63dced2a665ebc0b2abe2fcea6dc9f458fa7(
    value: typing.Optional[DataDatabricksClusterClusterInfoDriver],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68ced940de52b31db12815d33e7cb6bca0a631385e40a83f80940ddf1c04a861(
    *,
    host_private_ip: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    node_aws_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    node_id: typing.Optional[builtins.str] = None,
    private_ip: typing.Optional[builtins.str] = None,
    public_dns: typing.Optional[builtins.str] = None,
    start_timestamp: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7bd3aa065b6d5e534326758510259e2d950aa996aeb5d2501b88c9081bec549(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1a3fdbfa2f18fe2275334a1f3878050cba03a7acf573bf3f4172092b71cd639(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e2fbb17f19c1b0972057ee7810e71b2da1609f8034fcf9e86e46157f878b60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__578633b5dc86ecaee9997001abb099125ac498a297889551b6cf384a5f420a88(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08ba83c29cc5dae5d8337b607c115779b090527175ee6f894305984d436ecf96(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f75cd622b98d119eba41bd5a7e0746da030f23d7b4a744cbbcf2a8c47b58c29a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoExecutors]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea4fd17208a88155a5a8030d28ccd234937e79ee10760a1eacd8d8b64ecac61c(
    *,
    is_spot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b51a2a53f182bb38c9341a462531fc37088c69f56b614c28e9eaea85c0c676ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e933cb9af7cc5bf6388d45ba04942e1604a145abf869e03057589720f65ed044(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfe1cf24479428185d3d3d9816adb271579f8fa4a73a4908067b4a43417b47c1(
    value: typing.Optional[DataDatabricksClusterClusterInfoExecutorsNodeAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794e44d680e36d45e3f9ad57a343dbb3667b313026f04670a5983843a2040da3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a59ddda92d58e03b9020b80a222d7d1b6b0ea137f918608fe3efaebf269763a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49b9ffc3075332a8dc11936c90b574c720e172a74ca47711774f14207b814c9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5465a4e0196e45c63f04569c23cd7bf9754d05d42e1c8c2351433aca95d32196(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac1b67608952025fc443fc8b4783edcd5902a8685be001d1961b0212d9a2616(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc3109f80bb63adf9b3a969f529f050cb93b7b5c40cfb7994851e65c6b5a58c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d700fbfb34a8b44c99bb388afbb3a51849ee8cd93abbf63ce4c450ec10bb8bfd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63620a0f204d78f9e67fcf784f90bc6904678d678e7b7d13dc6e68363a855b2f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoExecutors]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85df097f450b27adaa3edd52f3d9beb9ccd2aaa8d69e14dc607a5b8fa3294cc3(
    *,
    availability: typing.Optional[builtins.str] = None,
    boot_disk_size: typing.Optional[jsii.Number] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    google_service_account: typing.Optional[builtins.str] = None,
    local_ssd_count: typing.Optional[jsii.Number] = None,
    use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b5ea7dea4b4d797090941398d6e37fe06fb757f70ec9b49738262c1250dd791(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df804ebf4b5c81cd88762d5f58e8e94d70e965d7cccbb6a83ffd40852d1b42be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d369c4a4894a5986f367a8d9ddc89ffec379c6a01d84960dba8f31636f1b55ab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570627fc8ab2c5f472c7fb053e3551c75ca437434a212058ce36d434183da550(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f2daf34b1b8730a16da7586ef1f70bddb52054b9128cd825a49a4b794da4f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cadccf360d499e9e77a0361aa3b342374d7cb001aeaee850cd94898936c92be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cc0389609f43b79c8a61bd119ebb3ac1b108126603410c0bfca31eb4feadce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79c663ae159db23aad58c80629cb05607779c3fc6a415c7bdcab68c700caf7b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15bf4d4d97a125c1039e84ea00a60b4fb7a110154849228f6f1aaae9ccf17f09(
    value: typing.Optional[DataDatabricksClusterClusterInfoGcpAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec251c56f5f0ef33a2270f603e47796ff276953e777a2c2cf10fd5ca203f6d3(
    *,
    abfss: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsAbfss, typing.Dict[builtins.str, typing.Any]]] = None,
    dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    file: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsFile, typing.Dict[builtins.str, typing.Any]]] = None,
    gcs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsGcs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoInitScriptsWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea52d24a26a99bb2d548e021e8013a737945380c3d5e4447069818bbde511d5(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84a8509d164f3550fb296dbfbef0d8b33c90593377d7667998c82dc0ec767bc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf5f65a506056abb7d7378e596d10a75039fa89eb4e64ad32048b7623a5413c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e9d562c80036b5c0c9f22071f2e546d1df5acec902074629708c098e574e44(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsAbfss],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d67109009094a4deab6e1d4b67f58a1b9ae50f97003149acd85746b67868fe30(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81631ac7e39fe2dcc22e09cf1981897487152fbea5e8d1b1ff09f7bf07e9f9d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ff45f4409a7c97daa2a553b93f301139b2b3c5f787f634e1e109c2d285d82f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b643a385874da4bf6775f582cd51fe7fd53e462c7340d969af43b9c835b981(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6771747ca7e1f7b5f816c9e39227a9c96726535d79bcec3c5afa25d9fe0dce4(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__186d3bc84c901d510186859f0d6260b903f2f80140fc139e1db36ec32e22b4e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd17c07d32237bacc6ed145052d7683e422bd24352d91838ceba4892ac5f6a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19eb9cb25b762d30e06b23d6982aad1ef9888793ef1d32c1a60479cb5eeff222(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsFile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8119a1c44a9d33e309c789fe4012db8fbf552c9dc8db2f3958ff3d6f7740939(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f142ac7d25678eccc9a142c4d0adce30330708c4fb7e549abaa2ace92f7d38d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e18a83c0ab521c040d58d70296579e447f4755a06bfdd51ce015c69459d138(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cedef98dc63d1d5a2d44d1eab9b885c74e1a30cfbfda138d7dd613c6f2320ed8(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsGcs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0896191ec64d6765caa2b8e3b84ae4e3928ddcd86d246ced1e45aa852e76b1c5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb866e116272148460e1709a8c4f773d4d2be27bf28f78cd8f0f104e5143b45f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9b1ffd84c1011a333e06c61385c6a356125ff9deda17dc87174aac90a808b11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7de68bc3bfcd803101f29b30ee77e7e5c8a40df06f06f504ca99baf7215b21(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e549cbcfc2730dab1c5a70191067d66936393a6e5a58ca4b6fb5e1c1eeba492d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d38ff722c9fb51e122c8c3098c072c0bb17458c6d0dd81ee6da5257ae04759(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoInitScripts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5ad84eb29f7b84f43f234d53bc39c6a83e6157df2a7d7f9d411025001d7f62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b46104a6bc3a5a0bb0d04c89fe99c3ac21a8b4dfbe0d9d3ee61667c92fcff6c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoInitScripts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de6bdda243f03c63317190e2fa6a90f5ecad11a838cea6269d710d0b00cbbf89(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99a3af6ad7a0874b5c2ba8b9f1ead79f393744d63ec93822f574f48eafc53a49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b1f77d1d8f129043e42463c6b553be965ab906e6cb4ec3e2622c28f98898920(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa340dc44e54714f7044c8864ecd1b714218b029439c0a1b5c8f89d234a3eae8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22fef37dbdc0c9a000effe467db1351cff646f9e19578466f246f10dfd82d4b8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2f707d92827505404bccbc1220f682877a61ce1eb5d8d360caa463df02246c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ebc84c825d1cada3a2a484af58612baa9003991320a57735e82d3e7bb168aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__480e912c3f3f1bc40949a7f07f427b9f8fbe1536dcbcb227abdbdf6cae809e97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__360c3b80e269927746a6ce6f5a995a7d451b5d2e2b27effb6a6f5e697a9a5522(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2efe4deed92debc3489555cb6d03914a8bc3ea80e3a3d154ad3e2c0acd0d87b1(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b2a2888be6b8322c0dac27494901cf734b9bac801e0de61459988d789871308(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a11ec869270e1ee1e91ea5592c26d4b7b0418690af3aa98492825fc64edd48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ff6d30880891dbdedd76b28aedca1f14e25a4a806b5d00e35459b8c82ab4584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5463eaeac134db73a89b89ac7a5f5a9af45810e1e7de2fd975b960f9bc04cf2(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd52f4c0f71e106d7562a553714e191d168c90273dace00150df66f27ea7f91(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f89bd0ece3554024f9c2e4fc487aff29b253dcc7c55e3df1a28010b485a8cbd6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a5d03358a356128c0b8606c98eaaa1036af545031711de5f030ecb137944c89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e26e6a50ceb29ec2beb9f73a973a1a704818ebb128a4192fced05b41126be68(
    value: typing.Optional[DataDatabricksClusterClusterInfoInitScriptsWorkspace],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a5c3229869d17b8538244b0fdd11725325d1a4fda2e92d873648bcfc84af2cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea4dba3a385208fb13805fadd1f155550c32ce064bad6368b3552ec8ea414924(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoExecutors, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb57a0d04bc6f0fe19afe3d5dece9516db82abd4de0cc090395cb4349372bea0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoInitScripts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22121b91bd4014ea1c111063accbe2fcff7b706536a17408326c22c59ece23f0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03db98a9820b5b21f508013c38284758670d05dea19de653e35c86a6af9b8871(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15d6e1915ec10f28cf0442ccb18bdc25429b5cbfe36a6d916168de159209ea06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f86145d9f6a8b67abe506e589523463bf2f6ab39326a24a5218fb7ed6011ce(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a9b58ff1c6bbf8bfcb6987139edf512379e2fe382bca0d6e54086eaaec9f97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68cb61f4e419bd8ada9dd7fd086ad784b217bc959cddc3b85f631f69a433f055(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31b37e9eccc44dab6d644af18d605f326841bd3bbd84fc7077a3dc46622bffe0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7fc76b37a2344f7dc3fa1e30ff8dd6c0b355f384fd6a03f706fd0a98fb18133(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41366137ff035417d9e13cf6cead0550b62e987e06afaded60d1a2e6b3dfab62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def4a2e6601323908a266d721257bc0b5df9a86d95e565037241c75745b6fe55(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f09485e0c6efdcef7ee9203ea9184b140b7edb5c0f7c9c8d78104541288dfac0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246b214c1e0a6af3c91c9ba3b94a919eca345fa37d30bde494cc884bb87eab37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd10f2c0131bee7282573acd48ccd0008fb0ecfa286b5691aa3243a54927b4c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57df41759dad7726fd9beb5995fff437d3e29ad8dc71545e8068ffcec8fae100(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21d03f96cf9c1a9413b4e0b13f175f44f0a82e16538ddc701b19f2d0e11c72c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d06ed51d59eae974c3ceef641c326c92888c62b8f2ef74d779426edb86b7f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72da05a9b56b01f50c0654805697f6c04ce188b2eb712db1948cc917a5069d3b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efbfa61a14c03be599ca26436983701cf9f4d325ba7b90665909f1fbe316648(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46f4dded366a647ec88392a5c521dbe7aa46383a34a1d8e75e209b695b78744(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e57b69bfb7f4c1832fca3fecee3b59b954cd85300b5bc7b99a673aa51ec93e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50b090777c2e59f174c04c46025064f4362ff18253fc25a76a2df90aed6413b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6aec61206fc698207291fca4b4b5fe4b42a5777d37e780be5873e22d249abcf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8e484c951fd458cca10605cd89905bc4548e9a51b8d702bae02d89373de09c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c02815a4129b7caa3178d6324d016315f6edeb7a7b25276f331f6d40709b10c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa92c977350a6bef48287ce2a6666b27c9c9a5eacc361eca7934b5b7f678fc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2215a4c7634eb1444c55048d14b27a51cddfabf211182b054794c0473cd8bb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb50e299d9342c6694edd25abec64c6e72a3a3cb4e34491fce28994c5a88d3e(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8473f32c0d37a0a58e04928313fb1e21b4b4dda8fc6cdd8a30beb1f5761ef5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e09b37cd8f3c047187ca1a05924812e0553aec526ed5110a2fe486ce117b1191(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c520ec003f8cca5a1439b11e26c25036c47b356b34363f2080f673d80902df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__809e7b8f4cbe076dec36d64d6d802d0291a14b875f81847cd7571ee69d2cc2be(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9684945163bfda726d2dd47510681d1789c0d4a3bd95271fb7d776a641064852(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fffa21e7caf53e99645e13e4ea1cfd6d41765d5b6a5bea56d5d112b1462d0fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd7eaebf00b101618eecb0adb8535fcb14575c7aa315b3385ada64de8ea4d35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d91e761ee85cd3837f32f6ea64eaabcbf3a984db59c7cb25790c38cbf5c7a96(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__752b90076eba86da3309f0b8a03d34859f847c197645e0964a8e563e81537d12(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f10ac7dea6b3ceaff0344a26cd17eb415162f54630339912ce949cc5e2746ab(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd3ff2999b11adebf3904d46bd1e1f111e4ce29eeb41862c0eff3638cc021870(
    value: typing.Optional[DataDatabricksClusterClusterInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b3d6502e1c7cc70d1c52b28d46cfa1bc967892f5044f8f4f56035e6b6a7ac6(
    *,
    apply_policy_default_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecAutoscale, typing.Dict[builtins.str, typing.Any]]] = None,
    aws_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_log_conf: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConf, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_mount_info: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecClusterMountInfo, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    data_security_mode: typing.Optional[builtins.str] = None,
    docker_image: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecDockerImage, typing.Dict[builtins.str, typing.Any]]] = None,
    driver_instance_pool_id: typing.Optional[builtins.str] = None,
    driver_node_type_id: typing.Optional[builtins.str] = None,
    enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gcp_attributes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    idempotency_token: typing.Optional[builtins.str] = None,
    init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecInitScripts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    is_single_node: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    kind: typing.Optional[builtins.str] = None,
    library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecLibrary, typing.Dict[builtins.str, typing.Any]]]]] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    num_workers: typing.Optional[jsii.Number] = None,
    policy_id: typing.Optional[builtins.str] = None,
    remote_disk_throughput: typing.Optional[jsii.Number] = None,
    runtime_engine: typing.Optional[builtins.str] = None,
    single_user_name: typing.Optional[builtins.str] = None,
    spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    spark_version: typing.Optional[builtins.str] = None,
    ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    total_initial_remote_disk_size: typing.Optional[jsii.Number] = None,
    use_ml_runtime: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    workload_type: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecWorkloadType, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cc8bb4fa18897c108e2775c2a93ce1b5278928bd022a47bc49950e5f985af4(
    *,
    max_workers: typing.Optional[jsii.Number] = None,
    min_workers: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595c205794605714edea3ab45ef074d3cadf2d7f23b1fd69e2c4f2c093a72df6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d9f16aa330d682bebab179ef6ea77f39fc99393f7153e43c2c11a2274e39c47(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e4dd149140f7a7ba62be16d5eff46aa0e9aa8a49a97c66c1a79cdd3e91460c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97794810df78630eb0da3fcda55e5d324af7f76e3985395304cacd17ec9d6a24(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecAutoscale],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ecae928782ae3f047a55cb1880eccce780bc0636694759bbf2089f19d6a547c(
    *,
    availability: typing.Optional[builtins.str] = None,
    ebs_volume_count: typing.Optional[jsii.Number] = None,
    ebs_volume_iops: typing.Optional[jsii.Number] = None,
    ebs_volume_size: typing.Optional[jsii.Number] = None,
    ebs_volume_throughput: typing.Optional[jsii.Number] = None,
    ebs_volume_type: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    spot_bid_price_percent: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47c80a7bc6c5f8491a32f9c5356e1109069e31af3a66680677c17eb053906675(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81cc8b98150b78ff5fc232c180a8b923a1471c7dc7f4caf16d9deb7cd3ee777(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bbc3709021f4fed3e3fb2cb1e4b7e1909c88ff243555840282dab10f58e8d7c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba8c27fcdd888b8e3bcda68ccf95141963b0edba89f573d476fec75d6cc8e12(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbce9dc31f1e434e04b32cdcb172d404c8de2383783454213f2aba06c0259026(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27641e6cac4d444c85cf8048ecccc46dd9a438e21c73d4c5074e44f35412c543(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8715d251b43cff2f181f206eff29a7c66f02fc70b8fd29a462ce5c2b6c8aa941(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9661a8baebc9d3542398c5d60f842bffeec5bff6d1b18316070cc753762eab77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__205658f1d48b8ec9a79e05345ff57cd1e0a3f77d61b49614e4bfd35c6b2863e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99699544b0536ac9af36b5c9206b8751e32cbb9dbf443892e76b2d45ab9a678(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d57abe78ba872b6ccc229467303ebc36db9c5d86ac5e85265c4a0e1577f75bf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d371501dae8e0a1cf30226302f232fd4b2e30b4cedf3bc920ba28bc24fff9f80(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9dfbdbbb261897455d062be8fd8ae6b4d8fd4fe8149d030ac1b8c9af6b0f031(
    *,
    availability: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    log_analytics_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_bid_max_price: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d322ff24ada47ee39a352a5c3a7a54697ed45cdc7eeb3a778f299128c80931a0(
    *,
    log_analytics_primary_key: typing.Optional[builtins.str] = None,
    log_analytics_workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04ec981d3bccdd0bcbe28342833170660bca4448c7aa4eed78fb24c0112dac9c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__851427dd6f70bb698a1fc4b632b3b058743f9b06ba343a396ee8dfd3e99641bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea37fad338206e178576866bba82f8e1987f1ee18d300d1c2c527a5263dd2af7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab26c9040e90d7e9d9f7f56becac300bc083bc671fde52fb13c2209e283ae01(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributesLogAnalyticsInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69640d1350917ccf2cf1a742e1a3520ed6453ed2a8da8ecc139d8419446c1150(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb39c8f68bd724f218d79e88c6ef0343ad59152a2a3dbd489d99ff879bde5da3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa67299c3a9d3548912482cc879bb8793247689a83aa08cb4b9e381b52564603(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35ba8591ef635a8761eb997006d11e4b8ac4dd20478c2294e4c6e4ee9545d20(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c941064a46dd7864bb83752399a4b3db8a58eec2f0ad7ec5a996d5e1c6d215e8(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecAzureAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a13616daf4806496e2e9fa7b381464c0d7dcb4bda905a86547de6a23e6636f7d(
    *,
    dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b584e866f92c444042fd00b721c885132dd48f4709c6b6f39ea3f8bdc0795089(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e67e62f77f6aa9cc5f1f8e55ed9412b07de9aa1feb9c5f4b32874274699f5cfd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaaedd79eff9704bdbe996eafa01b2f9c2928c413f0d01b3aca6a5157c2c7620(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e43525d56ee4d9194800d4bda307b99daa2a90a47dcc222e8948f9a0516335a0(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6081c454939049b69b508f7cfd467371730d208bd55d54511dded64dcfc77f9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bf0a5858abe66cf0e0e9b418633742e47eb068e87396f54ab58581c1b28b4f8(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConf],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbc8a9cd5ae7bdd68bebcbd75070bc1490d1f643ef56e5fa367f249ad67dd71(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5926873969070e217c7516c20da6cb6c0744aeb43fcc097cb8d1088fb3de052c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccf6d29d630861046bf42c93dcfce9b939bba2300440edb80a22ddf725cfe16e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fc2adbf614ea5bf7a9d312e5e1b0fca6bde00239126d374141ac29d426113b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba67f57d94a36bebb17fe4271887d4c5b1cb6c2374eed2548efdc5b05617e87a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cac116ee8ee76f6ccc063ebe31dc594fb170f87fe75b643228b755845836cd6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__699b4ab2a10f83685afa598c79494b8d4b248d6bb77c4135f3c42b04eb3a2ba4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02a59624879210257dde9af201beccfe07e03ed86f74a7ee74b8ce687f1f1475(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54f3ce9530f109cfd67b53874092e3b4f7523b1f4b02edb998680b814ea22542(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d69cd3a0b6824cc168ec7a606d216b5c0da6577cb44de0415b6de5fda3d96ec(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95edc15e4d409c36b975d55d0d55bd44ebc0ff11bed85d4fe685a675d5e0b30(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b658517c1fc0fcaf6fd37fde88596c31ed3138c3308da2da12fe1133601b6f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41950f1440c31374d5c3002bb9ac86cc7b312f2078a7170d9f994e927fd80635(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ee0931be92584250f0e6240e90e6846feefb518568704562f1cda2d20feea7a(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterLogConfVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b488567b953c2815a335abdbe68f30e01865bca02f880e5ea64a6677d20f84a2(
    *,
    local_mount_dir_path: builtins.str,
    network_filesystem_info: typing.Union[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo, typing.Dict[builtins.str, typing.Any]],
    remote_mount_dir_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0ade1ec3bf5f49ac641d2c2e2409f58b210183dba6bfd726e9259d504ff79ee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89041ab7aa69f0f0ac157416e5db117bacd70e5ce63e9fb6f98c40c8cd5e4d30(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c174feb0bee63bd9df97b6faef16926ecfcc7c67f258ee4cea2a258ca286cbec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c60deae8cf1f5e042226c3637f6de8e57716649b4e0c36c7a32077339e52a20a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d841f3bad4834ee7b51f22218b4f5b7d3f387ed0ad8802c6fa7c2caef6b8cc2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad071a800f9f3bac3a5cc6c70ec74734a38667de042b3e6d509e03bb3c933e77(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecClusterMountInfo]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1043c04f70eb880b8ac74a73a12d43654154aac875c06d6d658675bfee8cf109(
    *,
    server_address: builtins.str,
    mount_options: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971664711a9be665b563f37cad1a3c1e72e9a098db040431d37dc715709e3664(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a7e1376a05ae5f34375b918e9f8b030016203e0cfef2096267098a5d0860a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__019fafd26c8b88e32112d037c2c6cbfee7aaed6a67045f2dfade18a6f144bb68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fbdad5c1705d4bc0bdffedfc6549a3cf2c379036c44a197e1e99a7e1aca614b(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecClusterMountInfoNetworkFilesystemInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678c553415ca85e9685f4d7aeb23dc77d9fbec5dc848cd148fa778088f6f0349(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87e1803af40ddf249b38af8269ab0e474b032c08bb948fffd8225fd739ee917a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a26ce217fd2fb4c8aa59fc807f54381fe69aa3c47e615092da948d6720eff01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__375a3f0ec5de7c5d7f7328b2eb6271d71b8d7aaf20ebcc5f7797c02b32a56b45(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecClusterMountInfo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e002673d5c4f56c140c1c9b6a81cc14d8d1ff2359fa6da69a6e0b8609f5b83(
    *,
    url: builtins.str,
    basic_auth: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a2772f604a884df9f5f7e36c0ddf4ce2e55a19db83250164727b94a0970631(
    *,
    password: builtins.str,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43404cd7cb1b15cffce1e1f4772e39c3a40fb9af6fd15cb619de33c5425d276e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28656ddd600d5c6f795ac61e37ffc64b874df88660289d016f82ddacab68bf78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f362c187effef6217134fe8f395dd23d0089c76ebf35873964f74c62633f0c52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e74ebc54a764f156cbca18c777799ab6f3cd416ec91014c72d70d975f2f0fd2(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImageBasicAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dafb4fe145488329c4631ba2ae3abcc0817b4ea0b1826d5978325288c4d44835(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a44f60a5d1e4c29b7d0695ae55caeb71181f942a70ef19f38177b5f06b0d541(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e309f9d0da33507cd7789902afab655b20b028cf8d96f2d0433dadd900d70530(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecDockerImage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14fac0c0add21dfe40649adbb3775cade361afe5ee3841b2c683922e009cddcf(
    *,
    availability: typing.Optional[builtins.str] = None,
    boot_disk_size: typing.Optional[jsii.Number] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    google_service_account: typing.Optional[builtins.str] = None,
    local_ssd_count: typing.Optional[jsii.Number] = None,
    use_preemptible_executors: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e8ade5869e96e985c0680614d9ff55059205e67039c3bc146d166d4851cef09(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbca10cfd16397db3799cd5b99d49f670c68238668d187198bcab0246473fb4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dba0cf795371350e1ebbc8b1d1499984130bea81c166a221c5a94d94d6df54e1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31fc48287278156551bf20ea688291972ac51f88ec3e98cb7a730c93837af70b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad077c7f3e4d3770be19cda356d11a0ef04152de0519337a3c0b86552babd132(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a06d9bb4a6e648c98ee4564f3d007fde3f16594dd8e6bb11a1008d8acb1c1c2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e93f5fc257960aa45d71155b29b1742f4faa8c5ad9c0894c74e8b5393103978(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583f521ee2ac83d6de154c30823a3dc912321774ce7f8f795a435a8b88ccedd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b3665d18d18eacf5efa6161143ad4d38ccf6f88ea64c706d5c52c2d34d3711(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecGcpAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef31b7a6d03d8f598e1209dd9ed7ec231c05098571f6ebebe07bc341fd2df14a(
    *,
    abfss: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss, typing.Dict[builtins.str, typing.Any]]] = None,
    dbfs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    file: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsFile, typing.Dict[builtins.str, typing.Any]]] = None,
    gcs: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsGcs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__426ae4d552d798c02d723f8dd7ccba0b3c001456ca4b4d40c1222ccfb84a9ba4(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e1fd179941591e034f52d4ed908773d5a2069bef943748eb2582f5f509d40ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427b01852378d673a0a96026976176347d9179620181c255b33acd0ee1c5156e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f0c6292d959ff42606b88c5df4df20ad232d191596e71eb0a0854b631e47b54(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsAbfss],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__342a2b00c9fb0cdfc8d5e5d528af13ab4c86e62d0d9b665551b3db9f4bf60f07(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eb22efb0a36de0f60c2b16f7a3565b5f95744a0f2b8ba93fe61935716dc1416(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__928375090663b972dc99c916ee04aa8b361b016fb888b0e2d4c00a0eea60a553(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__042da1ee9a729226449d9a9d6c9a84f3849ff65687200df29c5ae29ac5716ebb(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a046ae6c44e52b2379874535ae4a3bbebc3e9ce4f3f38c6c4169dbb74347237e(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204208e7c129e91b12196ad1aedd4224618d9848e4764b76aad6da4902a872ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__800cd806c83775690b8ea7352e436c78bac30dffc1690b022389be37c2f29828(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69f62d81a5aa08c07c2574ff8e2f52d30c1c7f86a6f41086dcd45ad908fa8d9(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsFile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3bd930035d28dceceb7a2348a0e7f76b0aa875d038dc919b7c3b1dd372c633d(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26df2e984722355e9e45982a775b04c9c652247ca802f1a374130488c241555(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5534cc5ecabd38bad8512058217aff82e4143dba181ba2ae26c0e809373619(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cab1659ada805ed4b6ede430145f0b1ae5410378229651fd3040656a02acd3e(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsGcs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c103b13acecf83d2460523b7c70f5309f4c7cd20f613ee51c357916567248a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57cb160fc595ebdd5635763bb9e54f31da16cf64e7d34c68cca54f87fcb24f1f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d5b9bac118fbcaef4ed2c347b2c5f92c3e1d3e53a6f0f1ac8dcfd709f8f0ce6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05108bc2ff682ad25bcfd889faa1afa9c2ed5de249f8ba233121e6b3ea03e8d4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8849a6f5b9830d3ed6e18900ab16096a2e18902e2527bea12772c764675be8db(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__285fe8e1a904370a527cdbd9cf90d1233843027f49a4fed172b6ae4ab56f612c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecInitScripts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7bc56e69d88c620999c459800f87e6b2df32d5060e7eb0086802704512d29a0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a67aa60ddcd67222e28e3312f007cbb2e7e9a786ca567c0b14c56c71d85e7e3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecInitScripts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69fb16b3e54298324de65ef683c79c9bc8652d2f4296d4fb2c76a348174b350(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed399b83585e5b5ac781642a68b1c126ce1ef0a1bf3221d4b8efe38f7b282845(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5ee8352ca43b98eb85ca98226217d321e17ba905e666b9dd51daaa5da91f42d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a17043b1530995cf79ae38d43ceedfd455f83aef5751418d397fd55bd061a0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0223b1d1aee7fb13b711a49a84e8f8e7608f556263bdea0b9db3f850c205f9c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ff4f3f099f9b3bbd90aec96219a889318f6791e0928659c863a54a80ae03ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bbb3a24738023a33e93952311d5339b268d395af8f30125b761a1005b30cac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f508b012e37f2d6640a4bc2533beda57770065d66e529afe921c2b0e75741a65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d91c3293ffcbeb200ee3b4031ae53e537b3ab8ac98c477e02454478a9f0c51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d889bffa51104254b479536655f38a443dbdedc8d7849a9d1efecf3d8278fe(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__951cadf515dbf9838ae801ce297d01bae7ed599659932bced6318fa03daa6c26(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0630614bf797ace9f8120388cd2468b63b2ce3de5a1dba761ee85d5406e4f4d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4487424b01decb9e316bb962b9b081ce11035ff2862fd704fff22325f484e321(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d2137797a838b7f4471bb58301423d2ab5e1bd9411a4e1ed3488af0ab6b9556(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e180051c7101bdb272871950e7ac2a2e64df9de6228ae5c7aa7cb415cbca1940(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__700ffd105995af2b9e0ed98b43a4af3bc7542fb8274b58c11c12741e8da0c600(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c853e8710017bf51e138b654cca4f25a2a38e3d075da492b78ce4195f565ca08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9fc22dd440e97085a39364b253a8b6cb4534cf481403775c5427182c89b4a3b(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecInitScriptsWorkspace],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a8d7e81d9f48a581d582f69bf6729ea88c96e9db17b081076547dd696430da(
    *,
    cran: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecLibraryCran, typing.Dict[builtins.str, typing.Any]]] = None,
    egg: typing.Optional[builtins.str] = None,
    jar: typing.Optional[builtins.str] = None,
    maven: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecLibraryMaven, typing.Dict[builtins.str, typing.Any]]] = None,
    pypi: typing.Optional[typing.Union[DataDatabricksClusterClusterInfoSpecLibraryPypi, typing.Dict[builtins.str, typing.Any]]] = None,
    requirements: typing.Optional[builtins.str] = None,
    whl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98a1679f7867886515aa0766bed07cdd815d7cfa076ceb4d4062f86562b56fb(
    *,
    package: builtins.str,
    repo: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a5b98994c0e1d1e5e9a2a4d3490cad030c67f6f3928b6059dae3462552552d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a491fe354940615b4a9de7a7c568a20977dec1e4fefd08b84bbfd55c1bd27ff7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e16d0e9d004748376dbeb3fd82b06923a2f360c97d6394eeb28dda7dd0eb0d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11fe85067d65182ce692427b5ae4e9161a86041af610891bea4cde22412b4546(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryCran],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099be35d5268d1d9ed68b5b506dd8cc23b590135b2b9c047b0b9a99246a78277(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6f15388dc583e0021b3459ca1c945e2014799934bb75654327283dfd1aa1c0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46a2dbc4b1c50ea7b6eba7a1aff20f130e9cb81f1d0d3138ebcd56e708b3b12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58fb0a783d34dc295f3bee4022cbc001be80408f0c5949f6ab1c6fa914988a6f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9db4bb9eb94585dad51ace85b17aeda99b91b8904bad42567a235b16782199a1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9a02f482cd6a0623bed6917277b24f21798d1c150d03fca0beda5867b4b61af(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksClusterClusterInfoSpecLibrary]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c2dc804369a59330421c5ec70bb6ef5d12de204333e7f6bc27bac6ffc026df1(
    *,
    coordinates: builtins.str,
    exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    repo: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f71dcc43b3905dc2f41ff4afbee7e67bfeb5dd6a135805f8cfb4546ee77e1de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae0cb8dd60eb48040723067051ac773eaaf966f665eb23ac8bba24f9e7a6706(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a0f68c7cc405442eb8c4a175fea215bb51c4452bb0512e54d159f6485c26fd8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1807f614ac0a9a8f7d981473a8168781c90326a814e7be040e026d831ce20988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35bac5dbcc653e6fa53148f36a9e4fa33d061b2b4fd068f03b854e49930fbe87(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryMaven],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3174428114b345f0f8bf8f5e84dfd2787a3919d00ecd1bfb73f3b19b2e587726(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f5f189143af44cad333144b8f39fc0f8a27aa64dc4c26df982f72f69285649e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7cafcaac178bb838518f290bb9354ff09885cc9807c59e43430cac98767cd63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8652c5d96b7dab43808e4789dc0104ab2269092bb8ed5bea0f35c8f5cb3a87a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14fae7f2d4ed1d1c0803e94cd3319918a0c382d6b08efb1ab00040ff6980680f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9119f634533d10816a814225f1a387a233d97892a663994cdfb8ce821faeed4b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksClusterClusterInfoSpecLibrary]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dc47a8e625dbe20736e701bfe4557410c19e0d957567c48d2d29855e0b676d5(
    *,
    package: builtins.str,
    repo: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68b51b14bed25db7e22bb7e8c80923c96d3bd086f0e68cdc761a84049b91074(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e945f4ec9251a94dbc83c1b496928e328bba50aec59f8c7e1ac7b13907537fca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8f3b2ce6715ed1dbae49327364c5619b08cd9b2f877d1b7c6ea0e76d5f1d39e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157e7c168f2d5218c438a2e6ee49cf0ae3a4ca5a599154981be31803465934ae(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecLibraryPypi],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19bfd825a33b3d883f5245506fc983ffd68b33ed09e572e3d239b2ebf432ed8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a04837162fce5341fc2abaf18e96ecfb314391f154fff98ef037ae928b0d781(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecClusterMountInfo, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e137467d74213ca9021bd84cf8197be9ff6b40f180ab432479b58e1e829bd3c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecInitScripts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d85a66a5191937dd9bcb97be1c142244e7d853b0397d310a0970f187f32a1b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksClusterClusterInfoSpecLibrary, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5afbcc3c25f6ce4c96e8e167be30b9797f35232a06111a821a1efa010c788b4b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e5db786428fa3fee61394268fd49f8815387e375284a99c5c9980210c45e4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e33700fa94ba9a8101dea5fb5bb9135f6452c680dcb8fc0a7b76301d724b242(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba951d6a9111c09ccb8363b71e621e123cd72a50489de01e16ac5062b4cc464(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3d337f8e443f8f0ad575439badf32ee62c4c6fb649503638b1ddc58e6cda4cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f7b61ee021c6391b020506b58c50aebce87c7922c9e9be5f0cab139945f8b46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b29bd380315668bc65fa9448e1c0b5da73c1036f99175ac9638fc8572c5595(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d455d711ef049633c2f9955e8d8e4eb21970102cd27421776e52c8a159ecbb0d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0d9f807fc111dc623705ab471fa638879f6baeb2ef26a4247290d42cb5fac1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d434a16819a9d2bccde8c726679c0894180cba9f556778e8820dd9db681fef13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c44d9bc7690e324527952379db56f52f429aebfd7bd51dc617d0df03f084555(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__311b1e73eda77b31f3c4836e1cccacf70e35693b81bc8d56a3294feaa1db0903(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd99694443de18f9e011708fe5b5c2133f0e00a8adf97a69ebc1e8b80af5068(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c470e5ec4ddd3e13565296c1ee8b0f2512fd18dcd543f8f9b5ab004d5fddb24(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c736425080bca43855f5a70bb10c62c6f4f315d1db46495a82b638d937e03b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8caffcccb3069bb30778444e07cf07e287903be711e4a82562d24a81e79928bc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c13f5eff29c15ca06b42838c97a8156cb8ac591ab243c1fdb0137cff1983d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eeac916fa9c5218d0e4e2e4afdb55aedfe7552dae447f2b2911f184b16b0925(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__153fee277bd2f384cee55621fa220dee274ef71e37754085075214c6de91eed5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa3e3092ae2a5fcab6a3c40bda6e67bc31aa334e6c4ca58eeb7f881e8b962c0c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a28b808459d9ed2d2076d11df58347c51076164987c76cc0ff5a1fe05a09c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__045f1ba64894523c52e80aeed7184bf0bdfc192e22ed850a6abf21c3b8487ebd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31be5e42b41a7a14eeed51bba7642f502ee931ff49ec4a069667bca5addbab5d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1d585f8c279d923e30538939c53bb7938f46881ab651d2604c2142f65ae3f53(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__249bcb59dbbdb1492604acd69a1a0c3433d865b30409d6f7db6eb5016b728a1e(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__829609e77b5ab569a3822505894f51c66588de7c73a865a1f209a1c75f0a4ef1(
    *,
    clients: typing.Union[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b1e0ede642cc6c3ad2286ff3172c31e0be9b0d8a07bb24a8b50a00d9ad1b29(
    *,
    jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d663bf8125b4b36a12685e0ebcff7b379a095806b9a24cfd73cd464079d85dac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0ac3dac402b289a47da0e6979866ac49c00c717ac4ff2d2dc1d9142187bded(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__769be5f4897eb16ead30a07eace8cd1f19d2b95b09bb8e7c4dd022d8382ebc1d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4679170011a43ab31dc3b1627ecc549de9df5ec18b60699f8c51607b867e3d68(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadTypeClients],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23b94310b9420193325214a9412b09624c00bd87792a90e9be7c703ef961253(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be78376369f4796e732092b677594d6e47d89aabe0e0e070fa1c95fbf247d5d(
    value: typing.Optional[DataDatabricksClusterClusterInfoSpecWorkloadType],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd5c85764d53a6a4757976c6afb6b9b08b261d72a2016989577d23d61465207e(
    *,
    code: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__667dbbc3761b52f06c124e18c7baf96ce16c2927ba83bbf2f18ac82ce2033df5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d6facbb0e5042ca7ebb6859f6f9f9e9cb000005629a953b771383a3b2822d17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba9947e8c0a19dda024e1fee231e0704c4555511b63c76f04ae5a5733c60eee1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289d4bcfa3e10257d339406f9dbefb519145b6d376e481896452de7811e0ff21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccc5ff823ef83a3ee59591beae4019de81097d91ce6fa8f75b8a9f2eba9ddc04(
    value: typing.Optional[DataDatabricksClusterClusterInfoTerminationReason],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c52abaf00517d61ef032c48f79dc6da854a6fbca384b8ca84c798086f62ae2(
    *,
    clients: typing.Union[DataDatabricksClusterClusterInfoWorkloadTypeClients, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa910f7f39cfc7a8d092dcdf175efc21db164c0c8e89ef204576960bb17051e(
    *,
    jobs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notebooks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2eedbbdbcd36898ffda5a0192f44d059651e5e49a9e41a14c1b0dd597105887(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b65b820b13a2a14bf4592dd7c133176be553203f4a75afca82d41157c99e03bd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a39c8e5a10a63a592b1f27b73f03556d67e642bffec8e60946e8d1f0665d8177(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__878b69da8140018a03bc4b928ee6776b510c28002cef346ef2c5904de310a405(
    value: typing.Optional[DataDatabricksClusterClusterInfoWorkloadTypeClients],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f776185001279ec713db13590cb93b4ed3114f6202e6d0d6289027c494dabeaa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca10044f44f0d9fccb7e88992e90a2347f94ade9afb643a011594494d3f82194(
    value: typing.Optional[DataDatabricksClusterClusterInfoWorkloadType],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24360d74477cd67ee067f91407d4d0a33d77c869b9801fe22eca42b827f2e79(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    cluster_info: typing.Optional[typing.Union[DataDatabricksClusterClusterInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
