r'''
# `databricks_instance_pool`

Refer to the Terraform Registry for docs: [`databricks_instance_pool`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool).
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


class InstancePool(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePool",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool databricks_instance_pool}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        idle_instance_autotermination_minutes: jsii.Number,
        instance_pool_name: builtins.str,
        aws_attributes: typing.Optional[typing.Union["InstancePoolAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["InstancePoolAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disk_spec: typing.Optional[typing.Union["InstancePoolDiskSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["InstancePoolGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_pool_fleet_attributes: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_idle_instances: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["InstancePoolPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool databricks_instance_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param idle_instance_autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#idle_instance_autotermination_minutes InstancePool#idle_instance_autotermination_minutes}.
        :param instance_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_name InstancePool#instance_pool_name}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#aws_attributes InstancePool#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_attributes InstancePool#azure_attributes}
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#custom_tags InstancePool#custom_tags}.
        :param disk_spec: disk_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_spec InstancePool#disk_spec}
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#enable_elastic_disk InstancePool#enable_elastic_disk}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_attributes InstancePool#gcp_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#id InstancePool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_pool_fleet_attributes: instance_pool_fleet_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_fleet_attributes InstancePool#instance_pool_fleet_attributes}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_id InstancePool#instance_pool_id}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#max_capacity InstancePool#max_capacity}.
        :param min_idle_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#min_idle_instances InstancePool#min_idle_instances}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#node_type_id InstancePool#node_type_id}.
        :param preloaded_docker_image: preloaded_docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_docker_image InstancePool#preloaded_docker_image}
        :param preloaded_spark_versions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_spark_versions InstancePool#preloaded_spark_versions}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fe0669b730335f641cbfc73cb5d4d0d64b3119c518fa359cc5113e72d8e6d9f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = InstancePoolConfig(
            idle_instance_autotermination_minutes=idle_instance_autotermination_minutes,
            instance_pool_name=instance_pool_name,
            aws_attributes=aws_attributes,
            azure_attributes=azure_attributes,
            custom_tags=custom_tags,
            disk_spec=disk_spec,
            enable_elastic_disk=enable_elastic_disk,
            gcp_attributes=gcp_attributes,
            id=id,
            instance_pool_fleet_attributes=instance_pool_fleet_attributes,
            instance_pool_id=instance_pool_id,
            max_capacity=max_capacity,
            min_idle_instances=min_idle_instances,
            node_type_id=node_type_id,
            preloaded_docker_image=preloaded_docker_image,
            preloaded_spark_versions=preloaded_spark_versions,
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
        '''Generates CDKTF code for importing a InstancePool resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the InstancePool to import.
        :param import_from_id: The id of the existing InstancePool that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the InstancePool to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d966ac3085b0e2c05e84168258ea9a45b2503f2cac5a3f011af3678555152c09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAwsAttributes")
    def put_aws_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_price_percent InstancePool#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.
        '''
        value = InstancePoolAwsAttributes(
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
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_max_price InstancePool#spot_bid_max_price}.
        '''
        value = InstancePoolAzureAttributes(
            availability=availability, spot_bid_max_price=spot_bid_max_price
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAttributes", [value]))

    @jsii.member(jsii_name="putDiskSpec")
    def put_disk_spec(
        self,
        *,
        disk_count: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        disk_type: typing.Optional[typing.Union["InstancePoolDiskSpecDiskType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param disk_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_count InstancePool#disk_count}.
        :param disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_size InstancePool#disk_size}.
        :param disk_type: disk_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_type InstancePool#disk_type}
        '''
        value = InstancePoolDiskSpec(
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
        :param gcp_availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_availability InstancePool#gcp_availability}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#local_ssd_count InstancePool#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.
        '''
        value = InstancePoolGcpAttributes(
            gcp_availability=gcp_availability,
            local_ssd_count=local_ssd_count,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpAttributes", [value]))

    @jsii.member(jsii_name="putInstancePoolFleetAttributes")
    def put_instance_pool_fleet_attributes(
        self,
        *,
        launch_template_override: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride", typing.Dict[builtins.str, typing.Any]]]],
        fleet_on_demand_option: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributesFleetOnDemandOption", typing.Dict[builtins.str, typing.Any]]] = None,
        fleet_spot_option: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributesFleetSpotOption", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param launch_template_override: launch_template_override block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#launch_template_override InstancePool#launch_template_override}
        :param fleet_on_demand_option: fleet_on_demand_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_on_demand_option InstancePool#fleet_on_demand_option}
        :param fleet_spot_option: fleet_spot_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_spot_option InstancePool#fleet_spot_option}
        '''
        value = InstancePoolInstancePoolFleetAttributes(
            launch_template_override=launch_template_override,
            fleet_on_demand_option=fleet_on_demand_option,
            fleet_spot_option=fleet_spot_option,
        )

        return typing.cast(None, jsii.invoke(self, "putInstancePoolFleetAttributes", [value]))

    @jsii.member(jsii_name="putPreloadedDockerImage")
    def put_preloaded_docker_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["InstancePoolPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89538f73c16e4c86824bb70c2cc94fe2ddf4f45c7eca9b0333e461602e4e48e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPreloadedDockerImage", [value]))

    @jsii.member(jsii_name="resetAwsAttributes")
    def reset_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAttributes", []))

    @jsii.member(jsii_name="resetAzureAttributes")
    def reset_azure_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAttributes", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDiskSpec")
    def reset_disk_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSpec", []))

    @jsii.member(jsii_name="resetEnableElasticDisk")
    def reset_enable_elastic_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableElasticDisk", []))

    @jsii.member(jsii_name="resetGcpAttributes")
    def reset_gcp_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAttributes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="awsAttributes")
    def aws_attributes(self) -> "InstancePoolAwsAttributesOutputReference":
        return typing.cast("InstancePoolAwsAttributesOutputReference", jsii.get(self, "awsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributes")
    def azure_attributes(self) -> "InstancePoolAzureAttributesOutputReference":
        return typing.cast("InstancePoolAzureAttributesOutputReference", jsii.get(self, "azureAttributes"))

    @builtins.property
    @jsii.member(jsii_name="diskSpec")
    def disk_spec(self) -> "InstancePoolDiskSpecOutputReference":
        return typing.cast("InstancePoolDiskSpecOutputReference", jsii.get(self, "diskSpec"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributes")
    def gcp_attributes(self) -> "InstancePoolGcpAttributesOutputReference":
        return typing.cast("InstancePoolGcpAttributesOutputReference", jsii.get(self, "gcpAttributes"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolFleetAttributes")
    def instance_pool_fleet_attributes(
        self,
    ) -> "InstancePoolInstancePoolFleetAttributesOutputReference":
        return typing.cast("InstancePoolInstancePoolFleetAttributesOutputReference", jsii.get(self, "instancePoolFleetAttributes"))

    @builtins.property
    @jsii.member(jsii_name="preloadedDockerImage")
    def preloaded_docker_image(self) -> "InstancePoolPreloadedDockerImageList":
        return typing.cast("InstancePoolPreloadedDockerImageList", jsii.get(self, "preloadedDockerImage"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributesInput")
    def aws_attributes_input(self) -> typing.Optional["InstancePoolAwsAttributes"]:
        return typing.cast(typing.Optional["InstancePoolAwsAttributes"], jsii.get(self, "awsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributesInput")
    def azure_attributes_input(self) -> typing.Optional["InstancePoolAzureAttributes"]:
        return typing.cast(typing.Optional["InstancePoolAzureAttributes"], jsii.get(self, "azureAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSpecInput")
    def disk_spec_input(self) -> typing.Optional["InstancePoolDiskSpec"]:
        return typing.cast(typing.Optional["InstancePoolDiskSpec"], jsii.get(self, "diskSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="enableElasticDiskInput")
    def enable_elastic_disk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableElasticDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributesInput")
    def gcp_attributes_input(self) -> typing.Optional["InstancePoolGcpAttributes"]:
        return typing.cast(typing.Optional["InstancePoolGcpAttributes"], jsii.get(self, "gcpAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
    ) -> typing.Optional["InstancePoolInstancePoolFleetAttributes"]:
        return typing.cast(typing.Optional["InstancePoolInstancePoolFleetAttributes"], jsii.get(self, "instancePoolFleetAttributesInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolPreloadedDockerImage"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolPreloadedDockerImage"]]], jsii.get(self, "preloadedDockerImageInput"))

    @builtins.property
    @jsii.member(jsii_name="preloadedSparkVersionsInput")
    def preloaded_spark_versions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preloadedSparkVersionsInput"))

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc38d09fa55b09abdf8bb4b5bf1285825a43b515411fafda5eec385e228a8f12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__48f8fe7312dca01fc80cdde70ba093a6bcfb81b9b32c091bbe3021a75a015cef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableElasticDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f77a78c9072d8cf1a18435f10ab87fb46fa26415508605add32c64085e1fb32e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idleInstanceAutoterminationMinutes")
    def idle_instance_autotermination_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleInstanceAutoterminationMinutes"))

    @idle_instance_autotermination_minutes.setter
    def idle_instance_autotermination_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b243b2610bf2fc50c3f4c63bd52c3e2c66c63c8112392e85d9685b54b45cdc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleInstanceAutoterminationMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c75af596c1fa2fa2bf14a6a04ca05ded2756524af70c1b60166cf5cafb6f67c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolName")
    def instance_pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolName"))

    @instance_pool_name.setter
    def instance_pool_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c9939a3510d2fd667e37a6e8c75e186d2e7a8a04e470de00b5582cc78411bcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a495e1d65bbfc1c19a789ddc12c971b5c9705b3be9a7e3a77425de384a62e586)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minIdleInstances")
    def min_idle_instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minIdleInstances"))

    @min_idle_instances.setter
    def min_idle_instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f1415f496c0c40ba67ce74a82f7472f73b61a21dbcf4824bc8a220aad1ad809)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minIdleInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26774c282849d6b529a0fe39c15f5fe06b5a22cd43bd3ebfb4669771f5970e85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preloadedSparkVersions")
    def preloaded_spark_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preloadedSparkVersions"))

    @preloaded_spark_versions.setter
    def preloaded_spark_versions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aee2d9f6080d026bfe1b0a92c5136ec47fc1dade44fa0a4d8480644ad61c3f52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preloadedSparkVersions", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "spot_bid_price_percent": "spotBidPricePercent",
        "zone_id": "zoneId",
    },
)
class InstancePoolAwsAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_price_percent InstancePool#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abab87181c684ccbbffb56e898861fc378db26cb8f1efe333cd6c73cf06d5a2f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_price_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_price_percent InstancePool#spot_bid_price_percent}.'''
        result = self._values.get("spot_bid_price_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__948324a94f29420b78afa101fc9fb7da2f4e6d8b4338370327b7c215a3a7f868)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b41359e049f45b3737d55b3c8e363d82174e365fe37c313655e730660f96bea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercent")
    def spot_bid_price_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidPricePercent"))

    @spot_bid_price_percent.setter
    def spot_bid_price_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0417601934c48dc2c3d006912e26ede803363cd1eebbb4ccc384b2af32f87ccd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidPricePercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad7b12563098309b1911cdfc36d1b98bc59847fd37434a4fe60a4c8ee6d5dfb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InstancePoolAwsAttributes]:
        return typing.cast(typing.Optional[InstancePoolAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[InstancePoolAwsAttributes]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64579c057c919baec8b283d439136dd5d47fecafdc804dcfb4932c265360f49b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolAzureAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "spot_bid_max_price": "spotBidMaxPrice",
    },
)
class InstancePoolAzureAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_max_price InstancePool#spot_bid_max_price}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9cb38432ddda41d3bd409b6e01657aa65f2e7d0c21d083f6122a0db8d01e54c)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument spot_bid_max_price", value=spot_bid_max_price, expected_type=type_hints["spot_bid_max_price"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if spot_bid_max_price is not None:
            self._values["spot_bid_max_price"] = spot_bid_max_price

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability InstancePool#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_max_price(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#spot_bid_max_price InstancePool#spot_bid_max_price}.'''
        result = self._values.get("spot_bid_max_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolAzureAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolAzureAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolAzureAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8e393410536efa8f580eb7e0a420121416968f716b6dcd3d33af54c01a09352)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c78863358da8b51e619798a2cee901cc19bbcacc84edd4f90823068564dcbd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPrice")
    def spot_bid_max_price(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidMaxPrice"))

    @spot_bid_max_price.setter
    def spot_bid_max_price(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f93de5221bfb02f01225866bb66b09df9e234f2e83408f0bf4cd308d6f8f8266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidMaxPrice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InstancePoolAzureAttributes]:
        return typing.cast(typing.Optional[InstancePoolAzureAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolAzureAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ce80317a8d42f9cec3792795b011e03292dfd937c091f886443f4467d4ca64a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "idle_instance_autotermination_minutes": "idleInstanceAutoterminationMinutes",
        "instance_pool_name": "instancePoolName",
        "aws_attributes": "awsAttributes",
        "azure_attributes": "azureAttributes",
        "custom_tags": "customTags",
        "disk_spec": "diskSpec",
        "enable_elastic_disk": "enableElasticDisk",
        "gcp_attributes": "gcpAttributes",
        "id": "id",
        "instance_pool_fleet_attributes": "instancePoolFleetAttributes",
        "instance_pool_id": "instancePoolId",
        "max_capacity": "maxCapacity",
        "min_idle_instances": "minIdleInstances",
        "node_type_id": "nodeTypeId",
        "preloaded_docker_image": "preloadedDockerImage",
        "preloaded_spark_versions": "preloadedSparkVersions",
    },
)
class InstancePoolConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        idle_instance_autotermination_minutes: jsii.Number,
        instance_pool_name: builtins.str,
        aws_attributes: typing.Optional[typing.Union[InstancePoolAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union[InstancePoolAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disk_spec: typing.Optional[typing.Union["InstancePoolDiskSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["InstancePoolGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_pool_fleet_attributes: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_idle_instances: typing.Optional[jsii.Number] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["InstancePoolPreloadedDockerImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param idle_instance_autotermination_minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#idle_instance_autotermination_minutes InstancePool#idle_instance_autotermination_minutes}.
        :param instance_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_name InstancePool#instance_pool_name}.
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#aws_attributes InstancePool#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_attributes InstancePool#azure_attributes}
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#custom_tags InstancePool#custom_tags}.
        :param disk_spec: disk_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_spec InstancePool#disk_spec}
        :param enable_elastic_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#enable_elastic_disk InstancePool#enable_elastic_disk}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_attributes InstancePool#gcp_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#id InstancePool#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_pool_fleet_attributes: instance_pool_fleet_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_fleet_attributes InstancePool#instance_pool_fleet_attributes}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_id InstancePool#instance_pool_id}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#max_capacity InstancePool#max_capacity}.
        :param min_idle_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#min_idle_instances InstancePool#min_idle_instances}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#node_type_id InstancePool#node_type_id}.
        :param preloaded_docker_image: preloaded_docker_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_docker_image InstancePool#preloaded_docker_image}
        :param preloaded_spark_versions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_spark_versions InstancePool#preloaded_spark_versions}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aws_attributes, dict):
            aws_attributes = InstancePoolAwsAttributes(**aws_attributes)
        if isinstance(azure_attributes, dict):
            azure_attributes = InstancePoolAzureAttributes(**azure_attributes)
        if isinstance(disk_spec, dict):
            disk_spec = InstancePoolDiskSpec(**disk_spec)
        if isinstance(gcp_attributes, dict):
            gcp_attributes = InstancePoolGcpAttributes(**gcp_attributes)
        if isinstance(instance_pool_fleet_attributes, dict):
            instance_pool_fleet_attributes = InstancePoolInstancePoolFleetAttributes(**instance_pool_fleet_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54957c831b19f7505943602c0a4981340c18392f9c5da45bfd1ee4716d1a995e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument idle_instance_autotermination_minutes", value=idle_instance_autotermination_minutes, expected_type=type_hints["idle_instance_autotermination_minutes"])
            check_type(argname="argument instance_pool_name", value=instance_pool_name, expected_type=type_hints["instance_pool_name"])
            check_type(argname="argument aws_attributes", value=aws_attributes, expected_type=type_hints["aws_attributes"])
            check_type(argname="argument azure_attributes", value=azure_attributes, expected_type=type_hints["azure_attributes"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument disk_spec", value=disk_spec, expected_type=type_hints["disk_spec"])
            check_type(argname="argument enable_elastic_disk", value=enable_elastic_disk, expected_type=type_hints["enable_elastic_disk"])
            check_type(argname="argument gcp_attributes", value=gcp_attributes, expected_type=type_hints["gcp_attributes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_pool_fleet_attributes", value=instance_pool_fleet_attributes, expected_type=type_hints["instance_pool_fleet_attributes"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_idle_instances", value=min_idle_instances, expected_type=type_hints["min_idle_instances"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument preloaded_docker_image", value=preloaded_docker_image, expected_type=type_hints["preloaded_docker_image"])
            check_type(argname="argument preloaded_spark_versions", value=preloaded_spark_versions, expected_type=type_hints["preloaded_spark_versions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "idle_instance_autotermination_minutes": idle_instance_autotermination_minutes,
            "instance_pool_name": instance_pool_name,
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
        if aws_attributes is not None:
            self._values["aws_attributes"] = aws_attributes
        if azure_attributes is not None:
            self._values["azure_attributes"] = azure_attributes
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if disk_spec is not None:
            self._values["disk_spec"] = disk_spec
        if enable_elastic_disk is not None:
            self._values["enable_elastic_disk"] = enable_elastic_disk
        if gcp_attributes is not None:
            self._values["gcp_attributes"] = gcp_attributes
        if id is not None:
            self._values["id"] = id
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
    def idle_instance_autotermination_minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#idle_instance_autotermination_minutes InstancePool#idle_instance_autotermination_minutes}.'''
        result = self._values.get("idle_instance_autotermination_minutes")
        assert result is not None, "Required property 'idle_instance_autotermination_minutes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def instance_pool_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_name InstancePool#instance_pool_name}.'''
        result = self._values.get("instance_pool_name")
        assert result is not None, "Required property 'instance_pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_attributes(self) -> typing.Optional[InstancePoolAwsAttributes]:
        '''aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#aws_attributes InstancePool#aws_attributes}
        '''
        result = self._values.get("aws_attributes")
        return typing.cast(typing.Optional[InstancePoolAwsAttributes], result)

    @builtins.property
    def azure_attributes(self) -> typing.Optional[InstancePoolAzureAttributes]:
        '''azure_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_attributes InstancePool#azure_attributes}
        '''
        result = self._values.get("azure_attributes")
        return typing.cast(typing.Optional[InstancePoolAzureAttributes], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#custom_tags InstancePool#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def disk_spec(self) -> typing.Optional["InstancePoolDiskSpec"]:
        '''disk_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_spec InstancePool#disk_spec}
        '''
        result = self._values.get("disk_spec")
        return typing.cast(typing.Optional["InstancePoolDiskSpec"], result)

    @builtins.property
    def enable_elastic_disk(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#enable_elastic_disk InstancePool#enable_elastic_disk}.'''
        result = self._values.get("enable_elastic_disk")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gcp_attributes(self) -> typing.Optional["InstancePoolGcpAttributes"]:
        '''gcp_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_attributes InstancePool#gcp_attributes}
        '''
        result = self._values.get("gcp_attributes")
        return typing.cast(typing.Optional["InstancePoolGcpAttributes"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#id InstancePool#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_pool_fleet_attributes(
        self,
    ) -> typing.Optional["InstancePoolInstancePoolFleetAttributes"]:
        '''instance_pool_fleet_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_fleet_attributes InstancePool#instance_pool_fleet_attributes}
        '''
        result = self._values.get("instance_pool_fleet_attributes")
        return typing.cast(typing.Optional["InstancePoolInstancePoolFleetAttributes"], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pool_id InstancePool#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#max_capacity InstancePool#max_capacity}.'''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_idle_instances(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#min_idle_instances InstancePool#min_idle_instances}.'''
        result = self._values.get("min_idle_instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#node_type_id InstancePool#node_type_id}.'''
        result = self._values.get("node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preloaded_docker_image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolPreloadedDockerImage"]]]:
        '''preloaded_docker_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_docker_image InstancePool#preloaded_docker_image}
        '''
        result = self._values.get("preloaded_docker_image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolPreloadedDockerImage"]]], result)

    @builtins.property
    def preloaded_spark_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#preloaded_spark_versions InstancePool#preloaded_spark_versions}.'''
        result = self._values.get("preloaded_spark_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolDiskSpec",
    jsii_struct_bases=[],
    name_mapping={
        "disk_count": "diskCount",
        "disk_size": "diskSize",
        "disk_type": "diskType",
    },
)
class InstancePoolDiskSpec:
    def __init__(
        self,
        *,
        disk_count: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        disk_type: typing.Optional[typing.Union["InstancePoolDiskSpecDiskType", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param disk_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_count InstancePool#disk_count}.
        :param disk_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_size InstancePool#disk_size}.
        :param disk_type: disk_type block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_type InstancePool#disk_type}
        '''
        if isinstance(disk_type, dict):
            disk_type = InstancePoolDiskSpecDiskType(**disk_type)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fe595555d918d0e1f63fa63f9cc8c82a2f5d2df33cd63f94b45769b66d172d3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_count InstancePool#disk_count}.'''
        result = self._values.get("disk_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_size InstancePool#disk_size}.'''
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_type(self) -> typing.Optional["InstancePoolDiskSpecDiskType"]:
        '''disk_type block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#disk_type InstancePool#disk_type}
        '''
        result = self._values.get("disk_type")
        return typing.cast(typing.Optional["InstancePoolDiskSpecDiskType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolDiskSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolDiskSpecDiskType",
    jsii_struct_bases=[],
    name_mapping={
        "azure_disk_volume_type": "azureDiskVolumeType",
        "ebs_volume_type": "ebsVolumeType",
    },
)
class InstancePoolDiskSpecDiskType:
    def __init__(
        self,
        *,
        azure_disk_volume_type: typing.Optional[builtins.str] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param azure_disk_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_disk_volume_type InstancePool#azure_disk_volume_type}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#ebs_volume_type InstancePool#ebs_volume_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96095f98a845c22baac0b03aa9a9da396110ac6e3ae7fb2ae10bdd21a5de576)
            check_type(argname="argument azure_disk_volume_type", value=azure_disk_volume_type, expected_type=type_hints["azure_disk_volume_type"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if azure_disk_volume_type is not None:
            self._values["azure_disk_volume_type"] = azure_disk_volume_type
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type

    @builtins.property
    def azure_disk_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_disk_volume_type InstancePool#azure_disk_volume_type}.'''
        result = self._values.get("azure_disk_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#ebs_volume_type InstancePool#ebs_volume_type}.'''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolDiskSpecDiskType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolDiskSpecDiskTypeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolDiskSpecDiskTypeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fee9a3e80803fa414cc2a8bef5c8dbc373ed3e3f26df847b11db53d4466f504)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d57ebe333d4f0af6d338a36f7dccb75f6986b608796bb431820548ba5e2d2944)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureDiskVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeType")
    def ebs_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ebsVolumeType"))

    @ebs_volume_type.setter
    def ebs_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6187aa5e0110fb95fe33650286219adecc2a575b0b2f9c35f10e0761c697a4f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InstancePoolDiskSpecDiskType]:
        return typing.cast(typing.Optional[InstancePoolDiskSpecDiskType], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolDiskSpecDiskType],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__265eb64b92baa2a05aced68b7b405211c69e8b35f925204227fe92439371675c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InstancePoolDiskSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolDiskSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ac6d56a6c36d5b58a7789f752ed8ad8c37d8b0600e71f466eef0e6cb4b3fcb0)
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
        :param azure_disk_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#azure_disk_volume_type InstancePool#azure_disk_volume_type}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#ebs_volume_type InstancePool#ebs_volume_type}.
        '''
        value = InstancePoolDiskSpecDiskType(
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
    def disk_type(self) -> InstancePoolDiskSpecDiskTypeOutputReference:
        return typing.cast(InstancePoolDiskSpecDiskTypeOutputReference, jsii.get(self, "diskType"))

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
    def disk_type_input(self) -> typing.Optional[InstancePoolDiskSpecDiskType]:
        return typing.cast(typing.Optional[InstancePoolDiskSpecDiskType], jsii.get(self, "diskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="diskCount")
    def disk_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskCount"))

    @disk_count.setter
    def disk_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427101576fa835b0e78a244b4172e6efbb3d68645d1a1b6f39f86be9e059ecd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskSize")
    def disk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskSize"))

    @disk_size.setter
    def disk_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2feeb21a32fab416725f40c9f3cc5a29a1f9e99cdd2f57f0dee198a0dd193d09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InstancePoolDiskSpec]:
        return typing.cast(typing.Optional[InstancePoolDiskSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[InstancePoolDiskSpec]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f2d49ef7f1f070d8da37840b2baaf95db23fd5a09dba0d3c01636bf96fce833)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolGcpAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "gcp_availability": "gcpAvailability",
        "local_ssd_count": "localSsdCount",
        "zone_id": "zoneId",
    },
)
class InstancePoolGcpAttributes:
    def __init__(
        self,
        *,
        gcp_availability: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param gcp_availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_availability InstancePool#gcp_availability}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#local_ssd_count InstancePool#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e367a1e6ab65840c437af67153fe50b648be2c5d5bda80f74083481fd1b440b5)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#gcp_availability InstancePool#gcp_availability}.'''
        result = self._values.get("gcp_availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#local_ssd_count InstancePool#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#zone_id InstancePool#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolGcpAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolGcpAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolGcpAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6536ad05e8e3b8d5cd64965c4397cec862de7842bba38c5043434d7fbc85400)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82e4e1bc55a421acb05c347857596d48ca2b6cf3a72168210faf1968bd1cdf1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpAvailability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cc9ac5e552757b43e4c6fa1ef7106383c93aa8df6be4f78100a144f13596e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e20ff14ad7e6159cacba18289e723e09a5d281aa5641c65077cead5ada1a54e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InstancePoolGcpAttributes]:
        return typing.cast(typing.Optional[InstancePoolGcpAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[InstancePoolGcpAttributes]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6505b7e8bdc28109d0650443cf1675212ea99b3bb2d68ea0059fc64177f7cfaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "launch_template_override": "launchTemplateOverride",
        "fleet_on_demand_option": "fleetOnDemandOption",
        "fleet_spot_option": "fleetSpotOption",
    },
)
class InstancePoolInstancePoolFleetAttributes:
    def __init__(
        self,
        *,
        launch_template_override: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride", typing.Dict[builtins.str, typing.Any]]]],
        fleet_on_demand_option: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributesFleetOnDemandOption", typing.Dict[builtins.str, typing.Any]]] = None,
        fleet_spot_option: typing.Optional[typing.Union["InstancePoolInstancePoolFleetAttributesFleetSpotOption", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param launch_template_override: launch_template_override block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#launch_template_override InstancePool#launch_template_override}
        :param fleet_on_demand_option: fleet_on_demand_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_on_demand_option InstancePool#fleet_on_demand_option}
        :param fleet_spot_option: fleet_spot_option block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_spot_option InstancePool#fleet_spot_option}
        '''
        if isinstance(fleet_on_demand_option, dict):
            fleet_on_demand_option = InstancePoolInstancePoolFleetAttributesFleetOnDemandOption(**fleet_on_demand_option)
        if isinstance(fleet_spot_option, dict):
            fleet_spot_option = InstancePoolInstancePoolFleetAttributesFleetSpotOption(**fleet_spot_option)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e828de979028bd5c681b5193f32a2d32ee4c65e81f21fd0de5aea222cfa021df)
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
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride"]]:
        '''launch_template_override block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#launch_template_override InstancePool#launch_template_override}
        '''
        result = self._values.get("launch_template_override")
        assert result is not None, "Required property 'launch_template_override' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride"]], result)

    @builtins.property
    def fleet_on_demand_option(
        self,
    ) -> typing.Optional["InstancePoolInstancePoolFleetAttributesFleetOnDemandOption"]:
        '''fleet_on_demand_option block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_on_demand_option InstancePool#fleet_on_demand_option}
        '''
        result = self._values.get("fleet_on_demand_option")
        return typing.cast(typing.Optional["InstancePoolInstancePoolFleetAttributesFleetOnDemandOption"], result)

    @builtins.property
    def fleet_spot_option(
        self,
    ) -> typing.Optional["InstancePoolInstancePoolFleetAttributesFleetSpotOption"]:
        '''fleet_spot_option block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#fleet_spot_option InstancePool#fleet_spot_option}
        '''
        result = self._values.get("fleet_spot_option")
        return typing.cast(typing.Optional["InstancePoolInstancePoolFleetAttributesFleetSpotOption"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolInstancePoolFleetAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesFleetOnDemandOption",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "instance_pools_to_use_count": "instancePoolsToUseCount",
    },
)
class InstancePoolInstancePoolFleetAttributesFleetOnDemandOption:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd477dae7da0f432614c1903343fd0ab6570faed56dc4e8aea325543f89eec2)
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument instance_pools_to_use_count", value=instance_pools_to_use_count, expected_type=type_hints["instance_pools_to_use_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }
        if instance_pools_to_use_count is not None:
            self._values["instance_pools_to_use_count"] = instance_pools_to_use_count

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_pools_to_use_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.'''
        result = self._values.get("instance_pools_to_use_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolInstancePoolFleetAttributesFleetOnDemandOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolInstancePoolFleetAttributesFleetOnDemandOptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesFleetOnDemandOptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__515da17f2fdde473bdb751e88c5298cbb85e7a4811ec5c22834f8ab1104064a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0e5c1d20d5af9afc57e2cf7bc6545af3c0442a1ad40ba24e902390ca019929e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allocationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCount")
    def instance_pools_to_use_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instancePoolsToUseCount"))

    @instance_pools_to_use_count.setter
    def instance_pools_to_use_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72344b1e6d12bd8c9a24377d6e38d9e25b67a7baef138ca1b2d6121cb8ed9a2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolsToUseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption]:
        return typing.cast(typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2499cb2d1c7216e564fa787d0cc0fcbf5ec131979746ea8af2c9b206ba926ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesFleetSpotOption",
    jsii_struct_bases=[],
    name_mapping={
        "allocation_strategy": "allocationStrategy",
        "instance_pools_to_use_count": "instancePoolsToUseCount",
    },
)
class InstancePoolInstancePoolFleetAttributesFleetSpotOption:
    def __init__(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d7d614fe662773028fb3f83eeff3dd97e753d95da44ed732d113ff0eecb5cb)
            check_type(argname="argument allocation_strategy", value=allocation_strategy, expected_type=type_hints["allocation_strategy"])
            check_type(argname="argument instance_pools_to_use_count", value=instance_pools_to_use_count, expected_type=type_hints["instance_pools_to_use_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allocation_strategy": allocation_strategy,
        }
        if instance_pools_to_use_count is not None:
            self._values["instance_pools_to_use_count"] = instance_pools_to_use_count

    @builtins.property
    def allocation_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.'''
        result = self._values.get("allocation_strategy")
        assert result is not None, "Required property 'allocation_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_pools_to_use_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.'''
        result = self._values.get("instance_pools_to_use_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolInstancePoolFleetAttributesFleetSpotOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolInstancePoolFleetAttributesFleetSpotOptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesFleetSpotOptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71b851d393fde2fcfd6a95a711937bda98de5b1ed6fcf56675595ef56741e7e2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf727d645b34e2a80eb6f8c5cb399082baaa1d11e81f85e5cdd19a2121a5b95f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allocationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolsToUseCount")
    def instance_pools_to_use_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instancePoolsToUseCount"))

    @instance_pools_to_use_count.setter
    def instance_pools_to_use_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a862f92674a1636f8f6d7f64078a85405f080067bb30282f69833f7abed633a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolsToUseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption]:
        return typing.cast(typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2028aadd9fb6d6af2efed222c462cc3512740d93422ca90458e1ae424722a42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone": "availabilityZone",
        "instance_type": "instanceType",
    },
)
class InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride:
    def __init__(
        self,
        *,
        availability_zone: builtins.str,
        instance_type: builtins.str,
    ) -> None:
        '''
        :param availability_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability_zone InstancePool#availability_zone}.
        :param instance_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_type InstancePool#instance_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eb4a6b6ba01854a8f50df8c6ecdee354b17404ca1b29150fef215dd2e33ecaa)
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone": availability_zone,
            "instance_type": instance_type,
        }

    @builtins.property
    def availability_zone(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#availability_zone InstancePool#availability_zone}.'''
        result = self._values.get("availability_zone")
        assert result is not None, "Required property 'availability_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_type InstancePool#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c908d2c32f036c1d85704f1732843a9572ca37638b0768e55144e0eaccf932e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0404d354279074c190ec04a488ef64996db88bff1be2f593da950e31470a928a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12e1a849fe9f150c0bdf9a0647772de918b68639cc7511670e873012b5551136)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd47dbb245fd952f5f7274f7b321bf915c9a97d473a0188dc3976e7a2e62050f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c95d24bd74700a630c45598621ebd513c304124a033a38f3ca62c60dd4e3ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66f87af3ea15fe1822fd2da01cbdc03b4d7da19b74372fb8cbd7710313fd26d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71d2d7f86d471a8f9b43ae22f3678cb58d4c8769d1d792cbdd055659bb1d27b8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a91ef62664f864d428abf8c70f2e5f25a9579e8240534add9ae9b440d90197c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6debbe2e583b227d85b0df9445600091cfa3819b8e84a46c44c8f4b0034cbda1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48f9cb15adce278083eb0a703e68a3fdcca191dcf5df81412485f8c7f9e0b8ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InstancePoolInstancePoolFleetAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolInstancePoolFleetAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58eed7269aab01160f1384daa6ec0ab48c8f8a9063e41611f2b4cf02ab345186)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putFleetOnDemandOption")
    def put_fleet_on_demand_option(
        self,
        *,
        allocation_strategy: builtins.str,
        instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.
        '''
        value = InstancePoolInstancePoolFleetAttributesFleetOnDemandOption(
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
        :param allocation_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#allocation_strategy InstancePool#allocation_strategy}.
        :param instance_pools_to_use_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#instance_pools_to_use_count InstancePool#instance_pools_to_use_count}.
        '''
        value = InstancePoolInstancePoolFleetAttributesFleetSpotOption(
            allocation_strategy=allocation_strategy,
            instance_pools_to_use_count=instance_pools_to_use_count,
        )

        return typing.cast(None, jsii.invoke(self, "putFleetSpotOption", [value]))

    @jsii.member(jsii_name="putLaunchTemplateOverride")
    def put_launch_template_override(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ae6029e4edf9f1a579eccd72847d603afbbab5192303af8adab99f7b18101e)
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
    ) -> InstancePoolInstancePoolFleetAttributesFleetOnDemandOptionOutputReference:
        return typing.cast(InstancePoolInstancePoolFleetAttributesFleetOnDemandOptionOutputReference, jsii.get(self, "fleetOnDemandOption"))

    @builtins.property
    @jsii.member(jsii_name="fleetSpotOption")
    def fleet_spot_option(
        self,
    ) -> InstancePoolInstancePoolFleetAttributesFleetSpotOptionOutputReference:
        return typing.cast(InstancePoolInstancePoolFleetAttributesFleetSpotOptionOutputReference, jsii.get(self, "fleetSpotOption"))

    @builtins.property
    @jsii.member(jsii_name="launchTemplateOverride")
    def launch_template_override(
        self,
    ) -> InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideList:
        return typing.cast(InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideList, jsii.get(self, "launchTemplateOverride"))

    @builtins.property
    @jsii.member(jsii_name="fleetOnDemandOptionInput")
    def fleet_on_demand_option_input(
        self,
    ) -> typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption]:
        return typing.cast(typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption], jsii.get(self, "fleetOnDemandOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="fleetSpotOptionInput")
    def fleet_spot_option_input(
        self,
    ) -> typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption]:
        return typing.cast(typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption], jsii.get(self, "fleetSpotOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="launchTemplateOverrideInput")
    def launch_template_override_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]], jsii.get(self, "launchTemplateOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[InstancePoolInstancePoolFleetAttributes]:
        return typing.cast(typing.Optional[InstancePoolInstancePoolFleetAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolInstancePoolFleetAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84532ee5856f692eef1c01e2b7e944df8b455911fe6d90a1adc0241f25cab472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolPreloadedDockerImage",
    jsii_struct_bases=[],
    name_mapping={"url": "url", "basic_auth": "basicAuth"},
)
class InstancePoolPreloadedDockerImage:
    def __init__(
        self,
        *,
        url: builtins.str,
        basic_auth: typing.Optional[typing.Union["InstancePoolPreloadedDockerImageBasicAuth", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#url InstancePool#url}.
        :param basic_auth: basic_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#basic_auth InstancePool#basic_auth}
        '''
        if isinstance(basic_auth, dict):
            basic_auth = InstancePoolPreloadedDockerImageBasicAuth(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c03ea5fe439a3a07df0a0ad17e55252cbc1cc35483e82a8daebf47c2e42a33d)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#url InstancePool#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth(
        self,
    ) -> typing.Optional["InstancePoolPreloadedDockerImageBasicAuth"]:
        '''basic_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#basic_auth InstancePool#basic_auth}
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["InstancePoolPreloadedDockerImageBasicAuth"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolPreloadedDockerImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolPreloadedDockerImageBasicAuth",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class InstancePoolPreloadedDockerImageBasicAuth:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#password InstancePool#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#username InstancePool#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a312b50d7a395d48450e27cce4bc9c1f1cbe7574cf0975465b3a8c4e7a21f54a)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#password InstancePool#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#username InstancePool#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstancePoolPreloadedDockerImageBasicAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstancePoolPreloadedDockerImageBasicAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolPreloadedDockerImageBasicAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1bcb05bce110788d257e7fe3f067ca3f7a5b096f6db32dc29067f1938a86034)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f47ad7a6dcbe7f5446b9bfe9c4415d7ca9c75d9410eb17957f5fce0f4ccabfd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a3b8c1837b68627d7cb268273b0fc3896611a2d1eef08b285981e9fdaecae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[InstancePoolPreloadedDockerImageBasicAuth]:
        return typing.cast(typing.Optional[InstancePoolPreloadedDockerImageBasicAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InstancePoolPreloadedDockerImageBasicAuth],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c5200ed29b09448f0365edaaf39517e80f70bebddb483e3e375f7df33c64904)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InstancePoolPreloadedDockerImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolPreloadedDockerImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6131bdbcc7a0d277935a3ed7bf53e5ebd7c837b63979b968ba1f67286015d20f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "InstancePoolPreloadedDockerImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d495d2f84f3937bd032d92bee73e1623ebb5f1fb11056d58eba1bea09a732c1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("InstancePoolPreloadedDockerImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__819509d5c4f9943ddca69c6f048dd5c274cdaccc434b187eaa8d78e11d4c99ee)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0314f782fe64da21edfc250448eb865a00effcea45c317114c24d9b906741f8c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1727efa8480562fceae1d51bfca181a056ab17921a4afb16adfe14fbfc09490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolPreloadedDockerImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolPreloadedDockerImage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolPreloadedDockerImage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a12a5650fb28cca280810f9c9fdd51f06745684ad96e79f68518692bc95aff1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InstancePoolPreloadedDockerImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.instancePool.InstancePoolPreloadedDockerImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc1a508f42f29bcb25e5434462b5c837b4f30fc6ce42cad31c04ee1b98456d7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putBasicAuth")
    def put_basic_auth(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#password InstancePool#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/instance_pool#username InstancePool#username}.
        '''
        value = InstancePoolPreloadedDockerImageBasicAuth(
            password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putBasicAuth", [value]))

    @jsii.member(jsii_name="resetBasicAuth")
    def reset_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicAuth", []))

    @builtins.property
    @jsii.member(jsii_name="basicAuth")
    def basic_auth(self) -> InstancePoolPreloadedDockerImageBasicAuthOutputReference:
        return typing.cast(InstancePoolPreloadedDockerImageBasicAuthOutputReference, jsii.get(self, "basicAuth"))

    @builtins.property
    @jsii.member(jsii_name="basicAuthInput")
    def basic_auth_input(
        self,
    ) -> typing.Optional[InstancePoolPreloadedDockerImageBasicAuth]:
        return typing.cast(typing.Optional[InstancePoolPreloadedDockerImageBasicAuth], jsii.get(self, "basicAuthInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__5c3a806883baa5c8dac6a05da8e1485d2188edf9eb319cfabc98111bf108df90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolPreloadedDockerImage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolPreloadedDockerImage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolPreloadedDockerImage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__533b62c9987e0ce6d8f715b626783c39f0a6d46bb866a99c2322007ff3560bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "InstancePool",
    "InstancePoolAwsAttributes",
    "InstancePoolAwsAttributesOutputReference",
    "InstancePoolAzureAttributes",
    "InstancePoolAzureAttributesOutputReference",
    "InstancePoolConfig",
    "InstancePoolDiskSpec",
    "InstancePoolDiskSpecDiskType",
    "InstancePoolDiskSpecDiskTypeOutputReference",
    "InstancePoolDiskSpecOutputReference",
    "InstancePoolGcpAttributes",
    "InstancePoolGcpAttributesOutputReference",
    "InstancePoolInstancePoolFleetAttributes",
    "InstancePoolInstancePoolFleetAttributesFleetOnDemandOption",
    "InstancePoolInstancePoolFleetAttributesFleetOnDemandOptionOutputReference",
    "InstancePoolInstancePoolFleetAttributesFleetSpotOption",
    "InstancePoolInstancePoolFleetAttributesFleetSpotOptionOutputReference",
    "InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride",
    "InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideList",
    "InstancePoolInstancePoolFleetAttributesLaunchTemplateOverrideOutputReference",
    "InstancePoolInstancePoolFleetAttributesOutputReference",
    "InstancePoolPreloadedDockerImage",
    "InstancePoolPreloadedDockerImageBasicAuth",
    "InstancePoolPreloadedDockerImageBasicAuthOutputReference",
    "InstancePoolPreloadedDockerImageList",
    "InstancePoolPreloadedDockerImageOutputReference",
]

publication.publish()

def _typecheckingstub__7fe0669b730335f641cbfc73cb5d4d0d64b3119c518fa359cc5113e72d8e6d9f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    idle_instance_autotermination_minutes: jsii.Number,
    instance_pool_name: builtins.str,
    aws_attributes: typing.Optional[typing.Union[InstancePoolAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[InstancePoolAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disk_spec: typing.Optional[typing.Union[InstancePoolDiskSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gcp_attributes: typing.Optional[typing.Union[InstancePoolGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_pool_fleet_attributes: typing.Optional[typing.Union[InstancePoolInstancePoolFleetAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    min_idle_instances: typing.Optional[jsii.Number] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolPreloadedDockerImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__d966ac3085b0e2c05e84168258ea9a45b2503f2cac5a3f011af3678555152c09(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89538f73c16e4c86824bb70c2cc94fe2ddf4f45c7eca9b0333e461602e4e48e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolPreloadedDockerImage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc38d09fa55b09abdf8bb4b5bf1285825a43b515411fafda5eec385e228a8f12(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f8fe7312dca01fc80cdde70ba093a6bcfb81b9b32c091bbe3021a75a015cef(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77a78c9072d8cf1a18435f10ab87fb46fa26415508605add32c64085e1fb32e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b243b2610bf2fc50c3f4c63bd52c3e2c66c63c8112392e85d9685b54b45cdc7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c75af596c1fa2fa2bf14a6a04ca05ded2756524af70c1b60166cf5cafb6f67c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c9939a3510d2fd667e37a6e8c75e186d2e7a8a04e470de00b5582cc78411bcd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a495e1d65bbfc1c19a789ddc12c971b5c9705b3be9a7e3a77425de384a62e586(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1415f496c0c40ba67ce74a82f7472f73b61a21dbcf4824bc8a220aad1ad809(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26774c282849d6b529a0fe39c15f5fe06b5a22cd43bd3ebfb4669771f5970e85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aee2d9f6080d026bfe1b0a92c5136ec47fc1dade44fa0a4d8480644ad61c3f52(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abab87181c684ccbbffb56e898861fc378db26cb8f1efe333cd6c73cf06d5a2f(
    *,
    availability: typing.Optional[builtins.str] = None,
    spot_bid_price_percent: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__948324a94f29420b78afa101fc9fb7da2f4e6d8b4338370327b7c215a3a7f868(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41359e049f45b3737d55b3c8e363d82174e365fe37c313655e730660f96bea1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0417601934c48dc2c3d006912e26ede803363cd1eebbb4ccc384b2af32f87ccd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7b12563098309b1911cdfc36d1b98bc59847fd37434a4fe60a4c8ee6d5dfb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64579c057c919baec8b283d439136dd5d47fecafdc804dcfb4932c265360f49b(
    value: typing.Optional[InstancePoolAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9cb38432ddda41d3bd409b6e01657aa65f2e7d0c21d083f6122a0db8d01e54c(
    *,
    availability: typing.Optional[builtins.str] = None,
    spot_bid_max_price: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e393410536efa8f580eb7e0a420121416968f716b6dcd3d33af54c01a09352(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c78863358da8b51e619798a2cee901cc19bbcacc84edd4f90823068564dcbd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f93de5221bfb02f01225866bb66b09df9e234f2e83408f0bf4cd308d6f8f8266(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ce80317a8d42f9cec3792795b011e03292dfd937c091f886443f4467d4ca64a(
    value: typing.Optional[InstancePoolAzureAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54957c831b19f7505943602c0a4981340c18392f9c5da45bfd1ee4716d1a995e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    idle_instance_autotermination_minutes: jsii.Number,
    instance_pool_name: builtins.str,
    aws_attributes: typing.Optional[typing.Union[InstancePoolAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[InstancePoolAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disk_spec: typing.Optional[typing.Union[InstancePoolDiskSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_elastic_disk: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gcp_attributes: typing.Optional[typing.Union[InstancePoolGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_pool_fleet_attributes: typing.Optional[typing.Union[InstancePoolInstancePoolFleetAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    min_idle_instances: typing.Optional[jsii.Number] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    preloaded_docker_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolPreloadedDockerImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    preloaded_spark_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fe595555d918d0e1f63fa63f9cc8c82a2f5d2df33cd63f94b45769b66d172d3(
    *,
    disk_count: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    disk_type: typing.Optional[typing.Union[InstancePoolDiskSpecDiskType, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96095f98a845c22baac0b03aa9a9da396110ac6e3ae7fb2ae10bdd21a5de576(
    *,
    azure_disk_volume_type: typing.Optional[builtins.str] = None,
    ebs_volume_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fee9a3e80803fa414cc2a8bef5c8dbc373ed3e3f26df847b11db53d4466f504(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d57ebe333d4f0af6d338a36f7dccb75f6986b608796bb431820548ba5e2d2944(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6187aa5e0110fb95fe33650286219adecc2a575b0b2f9c35f10e0761c697a4f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265eb64b92baa2a05aced68b7b405211c69e8b35f925204227fe92439371675c(
    value: typing.Optional[InstancePoolDiskSpecDiskType],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac6d56a6c36d5b58a7789f752ed8ad8c37d8b0600e71f466eef0e6cb4b3fcb0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427101576fa835b0e78a244b4172e6efbb3d68645d1a1b6f39f86be9e059ecd3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2feeb21a32fab416725f40c9f3cc5a29a1f9e99cdd2f57f0dee198a0dd193d09(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f2d49ef7f1f070d8da37840b2baaf95db23fd5a09dba0d3c01636bf96fce833(
    value: typing.Optional[InstancePoolDiskSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e367a1e6ab65840c437af67153fe50b648be2c5d5bda80f74083481fd1b440b5(
    *,
    gcp_availability: typing.Optional[builtins.str] = None,
    local_ssd_count: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6536ad05e8e3b8d5cd64965c4397cec862de7842bba38c5043434d7fbc85400(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e4e1bc55a421acb05c347857596d48ca2b6cf3a72168210faf1968bd1cdf1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc9ac5e552757b43e4c6fa1ef7106383c93aa8df6be4f78100a144f13596e09(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20ff14ad7e6159cacba18289e723e09a5d281aa5641c65077cead5ada1a54e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6505b7e8bdc28109d0650443cf1675212ea99b3bb2d68ea0059fc64177f7cfaa(
    value: typing.Optional[InstancePoolGcpAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e828de979028bd5c681b5193f32a2d32ee4c65e81f21fd0de5aea222cfa021df(
    *,
    launch_template_override: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
    fleet_on_demand_option: typing.Optional[typing.Union[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption, typing.Dict[builtins.str, typing.Any]]] = None,
    fleet_spot_option: typing.Optional[typing.Union[InstancePoolInstancePoolFleetAttributesFleetSpotOption, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd477dae7da0f432614c1903343fd0ab6570faed56dc4e8aea325543f89eec2(
    *,
    allocation_strategy: builtins.str,
    instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__515da17f2fdde473bdb751e88c5298cbb85e7a4811ec5c22834f8ab1104064a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0e5c1d20d5af9afc57e2cf7bc6545af3c0442a1ad40ba24e902390ca019929e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72344b1e6d12bd8c9a24377d6e38d9e25b67a7baef138ca1b2d6121cb8ed9a2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2499cb2d1c7216e564fa787d0cc0fcbf5ec131979746ea8af2c9b206ba926ad5(
    value: typing.Optional[InstancePoolInstancePoolFleetAttributesFleetOnDemandOption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d7d614fe662773028fb3f83eeff3dd97e753d95da44ed732d113ff0eecb5cb(
    *,
    allocation_strategy: builtins.str,
    instance_pools_to_use_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71b851d393fde2fcfd6a95a711937bda98de5b1ed6fcf56675595ef56741e7e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf727d645b34e2a80eb6f8c5cb399082baaa1d11e81f85e5cdd19a2121a5b95f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a862f92674a1636f8f6d7f64078a85405f080067bb30282f69833f7abed633a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2028aadd9fb6d6af2efed222c462cc3512740d93422ca90458e1ae424722a42(
    value: typing.Optional[InstancePoolInstancePoolFleetAttributesFleetSpotOption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eb4a6b6ba01854a8f50df8c6ecdee354b17404ca1b29150fef215dd2e33ecaa(
    *,
    availability_zone: builtins.str,
    instance_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c908d2c32f036c1d85704f1732843a9572ca37638b0768e55144e0eaccf932e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0404d354279074c190ec04a488ef64996db88bff1be2f593da950e31470a928a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12e1a849fe9f150c0bdf9a0647772de918b68639cc7511670e873012b5551136(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd47dbb245fd952f5f7274f7b321bf915c9a97d473a0188dc3976e7a2e62050f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c95d24bd74700a630c45598621ebd513c304124a033a38f3ca62c60dd4e3ddb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66f87af3ea15fe1822fd2da01cbdc03b4d7da19b74372fb8cbd7710313fd26d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d2d7f86d471a8f9b43ae22f3678cb58d4c8769d1d792cbdd055659bb1d27b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a91ef62664f864d428abf8c70f2e5f25a9579e8240534add9ae9b440d90197c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6debbe2e583b227d85b0df9445600091cfa3819b8e84a46c44c8f4b0034cbda1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f9cb15adce278083eb0a703e68a3fdcca191dcf5df81412485f8c7f9e0b8ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58eed7269aab01160f1384daa6ec0ab48c8f8a9063e41611f2b4cf02ab345186(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ae6029e4edf9f1a579eccd72847d603afbbab5192303af8adab99f7b18101e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[InstancePoolInstancePoolFleetAttributesLaunchTemplateOverride, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84532ee5856f692eef1c01e2b7e944df8b455911fe6d90a1adc0241f25cab472(
    value: typing.Optional[InstancePoolInstancePoolFleetAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c03ea5fe439a3a07df0a0ad17e55252cbc1cc35483e82a8daebf47c2e42a33d(
    *,
    url: builtins.str,
    basic_auth: typing.Optional[typing.Union[InstancePoolPreloadedDockerImageBasicAuth, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a312b50d7a395d48450e27cce4bc9c1f1cbe7574cf0975465b3a8c4e7a21f54a(
    *,
    password: builtins.str,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1bcb05bce110788d257e7fe3f067ca3f7a5b096f6db32dc29067f1938a86034(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47ad7a6dcbe7f5446b9bfe9c4415d7ca9c75d9410eb17957f5fce0f4ccabfd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a3b8c1837b68627d7cb268273b0fc3896611a2d1eef08b285981e9fdaecae8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c5200ed29b09448f0365edaaf39517e80f70bebddb483e3e375f7df33c64904(
    value: typing.Optional[InstancePoolPreloadedDockerImageBasicAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6131bdbcc7a0d277935a3ed7bf53e5ebd7c837b63979b968ba1f67286015d20f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d495d2f84f3937bd032d92bee73e1623ebb5f1fb11056d58eba1bea09a732c1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__819509d5c4f9943ddca69c6f048dd5c274cdaccc434b187eaa8d78e11d4c99ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0314f782fe64da21edfc250448eb865a00effcea45c317114c24d9b906741f8c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1727efa8480562fceae1d51bfca181a056ab17921a4afb16adfe14fbfc09490(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a12a5650fb28cca280810f9c9fdd51f06745684ad96e79f68518692bc95aff1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[InstancePoolPreloadedDockerImage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc1a508f42f29bcb25e5434462b5c837b4f30fc6ce42cad31c04ee1b98456d7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c3a806883baa5c8dac6a05da8e1485d2188edf9eb319cfabc98111bf108df90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__533b62c9987e0ce6d8f715b626783c39f0a6d46bb866a99c2322007ff3560bb4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InstancePoolPreloadedDockerImage]],
) -> None:
    """Type checking stubs"""
    pass
