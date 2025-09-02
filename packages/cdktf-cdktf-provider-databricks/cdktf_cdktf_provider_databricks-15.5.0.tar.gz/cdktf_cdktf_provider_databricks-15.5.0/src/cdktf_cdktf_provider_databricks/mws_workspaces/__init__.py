r'''
# `databricks_mws_workspaces`

Refer to the Terraform Registry for docs: [`databricks_mws_workspaces`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces).
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


class MwsWorkspaces(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspaces",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces databricks_mws_workspaces}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: builtins.str,
        workspace_name: builtins.str,
        aws_region: typing.Optional[builtins.str] = None,
        cloud: typing.Optional[builtins.str] = None,
        cloud_resource_container: typing.Optional[typing.Union["MwsWorkspacesCloudResourceContainer", typing.Dict[builtins.str, typing.Any]]] = None,
        compute_mode: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        credentials_id: typing.Optional[builtins.str] = None,
        customer_managed_key_id: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        deployment_name: typing.Optional[builtins.str] = None,
        external_customer_info: typing.Optional[typing.Union["MwsWorkspacesExternalCustomerInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_managed_network_config: typing.Optional[typing.Union["MwsWorkspacesGcpManagedNetworkConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        gke_config: typing.Optional[typing.Union["MwsWorkspacesGkeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        is_no_public_ip_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        location: typing.Optional[builtins.str] = None,
        managed_services_customer_managed_key_id: typing.Optional[builtins.str] = None,
        network_id: typing.Optional[builtins.str] = None,
        pricing_tier: typing.Optional[builtins.str] = None,
        private_access_settings_id: typing.Optional[builtins.str] = None,
        storage_configuration_id: typing.Optional[builtins.str] = None,
        storage_customer_managed_key_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["MwsWorkspacesTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        token: typing.Optional[typing.Union["MwsWorkspacesToken", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[jsii.Number] = None,
        workspace_status: typing.Optional[builtins.str] = None,
        workspace_status_message: typing.Optional[builtins.str] = None,
        workspace_url: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces databricks_mws_workspaces} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#account_id MwsWorkspaces#account_id}.
        :param workspace_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_name MwsWorkspaces#workspace_name}.
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#aws_region MwsWorkspaces#aws_region}.
        :param cloud: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud MwsWorkspaces#cloud}.
        :param cloud_resource_container: cloud_resource_container block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud_resource_container MwsWorkspaces#cloud_resource_container}
        :param compute_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#compute_mode MwsWorkspaces#compute_mode}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#creation_time MwsWorkspaces#creation_time}.
        :param credentials_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#credentials_id MwsWorkspaces#credentials_id}.
        :param customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_managed_key_id MwsWorkspaces#customer_managed_key_id}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#custom_tags MwsWorkspaces#custom_tags}.
        :param deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#deployment_name MwsWorkspaces#deployment_name}.
        :param external_customer_info: external_customer_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#external_customer_info MwsWorkspaces#external_customer_info}
        :param gcp_managed_network_config: gcp_managed_network_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp_managed_network_config MwsWorkspaces#gcp_managed_network_config}
        :param gke_config: gke_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_config MwsWorkspaces#gke_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#id MwsWorkspaces#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_no_public_ip_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#is_no_public_ip_enabled MwsWorkspaces#is_no_public_ip_enabled}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#location MwsWorkspaces#location}.
        :param managed_services_customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#managed_services_customer_managed_key_id MwsWorkspaces#managed_services_customer_managed_key_id}.
        :param network_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#network_id MwsWorkspaces#network_id}.
        :param pricing_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#pricing_tier MwsWorkspaces#pricing_tier}.
        :param private_access_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#private_access_settings_id MwsWorkspaces#private_access_settings_id}.
        :param storage_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_configuration_id MwsWorkspaces#storage_configuration_id}.
        :param storage_customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_customer_managed_key_id MwsWorkspaces#storage_customer_managed_key_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#timeouts MwsWorkspaces#timeouts}
        :param token: token block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token MwsWorkspaces#token}
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_id MwsWorkspaces#workspace_id}.
        :param workspace_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status MwsWorkspaces#workspace_status}.
        :param workspace_status_message: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status_message MwsWorkspaces#workspace_status_message}.
        :param workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_url MwsWorkspaces#workspace_url}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__680d70784fa634cc71a9b01783e55bf3033a623db00c67733876b2e9afaf47c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MwsWorkspacesConfig(
            account_id=account_id,
            workspace_name=workspace_name,
            aws_region=aws_region,
            cloud=cloud,
            cloud_resource_container=cloud_resource_container,
            compute_mode=compute_mode,
            creation_time=creation_time,
            credentials_id=credentials_id,
            customer_managed_key_id=customer_managed_key_id,
            custom_tags=custom_tags,
            deployment_name=deployment_name,
            external_customer_info=external_customer_info,
            gcp_managed_network_config=gcp_managed_network_config,
            gke_config=gke_config,
            id=id,
            is_no_public_ip_enabled=is_no_public_ip_enabled,
            location=location,
            managed_services_customer_managed_key_id=managed_services_customer_managed_key_id,
            network_id=network_id,
            pricing_tier=pricing_tier,
            private_access_settings_id=private_access_settings_id,
            storage_configuration_id=storage_configuration_id,
            storage_customer_managed_key_id=storage_customer_managed_key_id,
            timeouts=timeouts,
            token=token,
            workspace_id=workspace_id,
            workspace_status=workspace_status,
            workspace_status_message=workspace_status_message,
            workspace_url=workspace_url,
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
        '''Generates CDKTF code for importing a MwsWorkspaces resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MwsWorkspaces to import.
        :param import_from_id: The id of the existing MwsWorkspaces that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MwsWorkspaces to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__518bc06e0416f074d4a3dac70d4d25963991149f96d1bbce4c5031b215201f4c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCloudResourceContainer")
    def put_cloud_resource_container(
        self,
        *,
        gcp: typing.Union["MwsWorkspacesCloudResourceContainerGcp", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param gcp: gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp MwsWorkspaces#gcp}
        '''
        value = MwsWorkspacesCloudResourceContainer(gcp=gcp)

        return typing.cast(None, jsii.invoke(self, "putCloudResourceContainer", [value]))

    @jsii.member(jsii_name="putExternalCustomerInfo")
    def put_external_customer_info(
        self,
        *,
        authoritative_user_email: builtins.str,
        authoritative_user_full_name: builtins.str,
        customer_name: builtins.str,
    ) -> None:
        '''
        :param authoritative_user_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_email MwsWorkspaces#authoritative_user_email}.
        :param authoritative_user_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_full_name MwsWorkspaces#authoritative_user_full_name}.
        :param customer_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_name MwsWorkspaces#customer_name}.
        '''
        value = MwsWorkspacesExternalCustomerInfo(
            authoritative_user_email=authoritative_user_email,
            authoritative_user_full_name=authoritative_user_full_name,
            customer_name=customer_name,
        )

        return typing.cast(None, jsii.invoke(self, "putExternalCustomerInfo", [value]))

    @jsii.member(jsii_name="putGcpManagedNetworkConfig")
    def put_gcp_managed_network_config(
        self,
        *,
        subnet_cidr: builtins.str,
        gke_cluster_pod_ip_range: typing.Optional[builtins.str] = None,
        gke_cluster_service_ip_range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param subnet_cidr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#subnet_cidr MwsWorkspaces#subnet_cidr}.
        :param gke_cluster_pod_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_pod_ip_range MwsWorkspaces#gke_cluster_pod_ip_range}.
        :param gke_cluster_service_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_service_ip_range MwsWorkspaces#gke_cluster_service_ip_range}.
        '''
        value = MwsWorkspacesGcpManagedNetworkConfig(
            subnet_cidr=subnet_cidr,
            gke_cluster_pod_ip_range=gke_cluster_pod_ip_range,
            gke_cluster_service_ip_range=gke_cluster_service_ip_range,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpManagedNetworkConfig", [value]))

    @jsii.member(jsii_name="putGkeConfig")
    def put_gke_config(
        self,
        *,
        connectivity_type: typing.Optional[builtins.str] = None,
        master_ip_range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connectivity_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#connectivity_type MwsWorkspaces#connectivity_type}.
        :param master_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#master_ip_range MwsWorkspaces#master_ip_range}.
        '''
        value = MwsWorkspacesGkeConfig(
            connectivity_type=connectivity_type, master_ip_range=master_ip_range
        )

        return typing.cast(None, jsii.invoke(self, "putGkeConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#create MwsWorkspaces#create}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#read MwsWorkspaces#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#update MwsWorkspaces#update}.
        '''
        value = MwsWorkspacesTimeouts(create=create, read=read, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putToken")
    def put_token(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        lifetime_seconds: typing.Optional[jsii.Number] = None,
        token_id: typing.Optional[builtins.str] = None,
        token_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#comment MwsWorkspaces#comment}.
        :param lifetime_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#lifetime_seconds MwsWorkspaces#lifetime_seconds}.
        :param token_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_id MwsWorkspaces#token_id}.
        :param token_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_value MwsWorkspaces#token_value}.
        '''
        value = MwsWorkspacesToken(
            comment=comment,
            lifetime_seconds=lifetime_seconds,
            token_id=token_id,
            token_value=token_value,
        )

        return typing.cast(None, jsii.invoke(self, "putToken", [value]))

    @jsii.member(jsii_name="resetAwsRegion")
    def reset_aws_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsRegion", []))

    @jsii.member(jsii_name="resetCloud")
    def reset_cloud(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloud", []))

    @jsii.member(jsii_name="resetCloudResourceContainer")
    def reset_cloud_resource_container(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudResourceContainer", []))

    @jsii.member(jsii_name="resetComputeMode")
    def reset_compute_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeMode", []))

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetCredentialsId")
    def reset_credentials_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialsId", []))

    @jsii.member(jsii_name="resetCustomerManagedKeyId")
    def reset_customer_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerManagedKeyId", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDeploymentName")
    def reset_deployment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentName", []))

    @jsii.member(jsii_name="resetExternalCustomerInfo")
    def reset_external_customer_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalCustomerInfo", []))

    @jsii.member(jsii_name="resetGcpManagedNetworkConfig")
    def reset_gcp_managed_network_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpManagedNetworkConfig", []))

    @jsii.member(jsii_name="resetGkeConfig")
    def reset_gke_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsNoPublicIpEnabled")
    def reset_is_no_public_ip_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsNoPublicIpEnabled", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @jsii.member(jsii_name="resetManagedServicesCustomerManagedKeyId")
    def reset_managed_services_customer_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedServicesCustomerManagedKeyId", []))

    @jsii.member(jsii_name="resetNetworkId")
    def reset_network_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkId", []))

    @jsii.member(jsii_name="resetPricingTier")
    def reset_pricing_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPricingTier", []))

    @jsii.member(jsii_name="resetPrivateAccessSettingsId")
    def reset_private_access_settings_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateAccessSettingsId", []))

    @jsii.member(jsii_name="resetStorageConfigurationId")
    def reset_storage_configuration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageConfigurationId", []))

    @jsii.member(jsii_name="resetStorageCustomerManagedKeyId")
    def reset_storage_customer_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCustomerManagedKeyId", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetWorkspaceId")
    def reset_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceId", []))

    @jsii.member(jsii_name="resetWorkspaceStatus")
    def reset_workspace_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceStatus", []))

    @jsii.member(jsii_name="resetWorkspaceStatusMessage")
    def reset_workspace_status_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceStatusMessage", []))

    @jsii.member(jsii_name="resetWorkspaceUrl")
    def reset_workspace_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceUrl", []))

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
    @jsii.member(jsii_name="cloudResourceContainer")
    def cloud_resource_container(
        self,
    ) -> "MwsWorkspacesCloudResourceContainerOutputReference":
        return typing.cast("MwsWorkspacesCloudResourceContainerOutputReference", jsii.get(self, "cloudResourceContainer"))

    @builtins.property
    @jsii.member(jsii_name="effectiveComputeMode")
    def effective_compute_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effectiveComputeMode"))

    @builtins.property
    @jsii.member(jsii_name="externalCustomerInfo")
    def external_customer_info(
        self,
    ) -> "MwsWorkspacesExternalCustomerInfoOutputReference":
        return typing.cast("MwsWorkspacesExternalCustomerInfoOutputReference", jsii.get(self, "externalCustomerInfo"))

    @builtins.property
    @jsii.member(jsii_name="gcpManagedNetworkConfig")
    def gcp_managed_network_config(
        self,
    ) -> "MwsWorkspacesGcpManagedNetworkConfigOutputReference":
        return typing.cast("MwsWorkspacesGcpManagedNetworkConfigOutputReference", jsii.get(self, "gcpManagedNetworkConfig"))

    @builtins.property
    @jsii.member(jsii_name="gcpWorkspaceSa")
    def gcp_workspace_sa(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpWorkspaceSa"))

    @builtins.property
    @jsii.member(jsii_name="gkeConfig")
    def gke_config(self) -> "MwsWorkspacesGkeConfigOutputReference":
        return typing.cast("MwsWorkspacesGkeConfigOutputReference", jsii.get(self, "gkeConfig"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MwsWorkspacesTimeoutsOutputReference":
        return typing.cast("MwsWorkspacesTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> "MwsWorkspacesTokenOutputReference":
        return typing.cast("MwsWorkspacesTokenOutputReference", jsii.get(self, "token"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsRegionInput")
    def aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudInput")
    def cloud_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudResourceContainerInput")
    def cloud_resource_container_input(
        self,
    ) -> typing.Optional["MwsWorkspacesCloudResourceContainer"]:
        return typing.cast(typing.Optional["MwsWorkspacesCloudResourceContainer"], jsii.get(self, "cloudResourceContainerInput"))

    @builtins.property
    @jsii.member(jsii_name="computeModeInput")
    def compute_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeModeInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialsIdInput")
    def credentials_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customerManagedKeyIdInput")
    def customer_managed_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerManagedKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentNameInput")
    def deployment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentNameInput"))

    @builtins.property
    @jsii.member(jsii_name="externalCustomerInfoInput")
    def external_customer_info_input(
        self,
    ) -> typing.Optional["MwsWorkspacesExternalCustomerInfo"]:
        return typing.cast(typing.Optional["MwsWorkspacesExternalCustomerInfo"], jsii.get(self, "externalCustomerInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpManagedNetworkConfigInput")
    def gcp_managed_network_config_input(
        self,
    ) -> typing.Optional["MwsWorkspacesGcpManagedNetworkConfig"]:
        return typing.cast(typing.Optional["MwsWorkspacesGcpManagedNetworkConfig"], jsii.get(self, "gcpManagedNetworkConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeConfigInput")
    def gke_config_input(self) -> typing.Optional["MwsWorkspacesGkeConfig"]:
        return typing.cast(typing.Optional["MwsWorkspacesGkeConfig"], jsii.get(self, "gkeConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="isNoPublicIpEnabledInput")
    def is_no_public_ip_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isNoPublicIpEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="managedServicesCustomerManagedKeyIdInput")
    def managed_services_customer_managed_key_id_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedServicesCustomerManagedKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="networkIdInput")
    def network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pricingTierInput")
    def pricing_tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pricingTierInput"))

    @builtins.property
    @jsii.member(jsii_name="privateAccessSettingsIdInput")
    def private_access_settings_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateAccessSettingsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="storageConfigurationIdInput")
    def storage_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="storageCustomerManagedKeyIdInput")
    def storage_customer_managed_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageCustomerManagedKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MwsWorkspacesTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "MwsWorkspacesTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional["MwsWorkspacesToken"]:
        return typing.cast(typing.Optional["MwsWorkspacesToken"], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceNameInput")
    def workspace_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceStatusInput")
    def workspace_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceStatusMessageInput")
    def workspace_status_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceStatusMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceUrlInput")
    def workspace_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05183b470223f1a801c482043e79dd1a7f20cd172aa38f610a28f8aeadcfd0a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43363e860473b0ea079f454bd682c51f6036c3dc8d131b5eac24e20779d80b83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloud")
    def cloud(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloud"))

    @cloud.setter
    def cloud(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d790cdd80ed5b547b7136dc048410b42785e63b739eb310a1e8633fd5f9220e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloud", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="computeMode")
    def compute_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeMode"))

    @compute_mode.setter
    def compute_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f989d6d4bc310dc6ee02488d35b48d2d42080ec12a247cc375d05af9e9bcf504)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edf7ae8f7248363260e62dd0aa468cc88bdcf49f49a56c3f8575cd57abb92340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="credentialsId")
    def credentials_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialsId"))

    @credentials_id.setter
    def credentials_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fccfe5f88c439d8057e3b68b42ec727fb0a9555904367175b039be8bd1c82bf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customerManagedKeyId")
    def customer_managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerManagedKeyId"))

    @customer_managed_key_id.setter
    def customer_managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9777a9f463fc23d1828441a45ce8551a356bb6b28bcdc6b280cfa64fab8e41b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerManagedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99367dddc1bcf9ce97a51e6dad244cd827c2312e00c7cd36ecebcf5198866ba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentName")
    def deployment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentName"))

    @deployment_name.setter
    def deployment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62115814f39c6a532d25455633af7d2300b6fc004a45d67006670d0d15491968)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48bd705e61f79ad72732eac80b5a9ad658b13cd2dadb54107b67f79fe2dfa733)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isNoPublicIpEnabled")
    def is_no_public_ip_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isNoPublicIpEnabled"))

    @is_no_public_ip_enabled.setter
    def is_no_public_ip_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b44147a5403101b5b43749310d5ab8dc27ece8a093f473cf0821686803051b7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isNoPublicIpEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fa84e5fd85d03f597c44a7eeb742ba52afd72d37c5f876120666053d77d73d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedServicesCustomerManagedKeyId")
    def managed_services_customer_managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedServicesCustomerManagedKeyId"))

    @managed_services_customer_managed_key_id.setter
    def managed_services_customer_managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__756262a9c3dc18683c02cdc7ae492bd506b7cb597f61ed90f6128100b1b2416f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedServicesCustomerManagedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkId")
    def network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkId"))

    @network_id.setter
    def network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70be8c2387d3570faa221e02a3c2325a65d5fac4d2632d0fae801a9f06b09a54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pricingTier")
    def pricing_tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pricingTier"))

    @pricing_tier.setter
    def pricing_tier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa3e99839f82c11f84f0c1de18d9bf17431eeffb61ed503bf65fa33b372f06af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pricingTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateAccessSettingsId")
    def private_access_settings_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateAccessSettingsId"))

    @private_access_settings_id.setter
    def private_access_settings_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd2462b71c0bb53845489d06e5951b4de783880d950c9ef2d9cd45ed7b654dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateAccessSettingsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageConfigurationId")
    def storage_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageConfigurationId"))

    @storage_configuration_id.setter
    def storage_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb1a300332b5f79f343d38d36175bab1a24d1b1325dfdc773ad27a88dd455b64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageCustomerManagedKeyId")
    def storage_customer_managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageCustomerManagedKeyId"))

    @storage_customer_managed_key_id.setter
    def storage_customer_managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9449fecc23d22668ccb3ea512166b1248dfa37eb9a348edaba0c70b06ca733b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageCustomerManagedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2544f921304b6aebf0c445e8883969a247b7119712590602bac474c902f3adb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceName")
    def workspace_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceName"))

    @workspace_name.setter
    def workspace_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e67996777048ad9adf8e32c192cc825f51904368b951e226f7c5ec7a15a86911)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceStatus")
    def workspace_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceStatus"))

    @workspace_status.setter
    def workspace_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdfca99cf8bce327fc8f51ff9cccaa31ddeff31421286cce7f01bdaa0f3de3dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceStatusMessage")
    def workspace_status_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceStatusMessage"))

    @workspace_status_message.setter
    def workspace_status_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f86fa9eb18a18969407c0c6e73fdd21b8033835c66f58053b280bae46c06105)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceStatusMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceUrl")
    def workspace_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceUrl"))

    @workspace_url.setter
    def workspace_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a86ecdbb85a4feacc361296916c0190e4e5954800e7fc4a0717bde53e69cd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceUrl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesCloudResourceContainer",
    jsii_struct_bases=[],
    name_mapping={"gcp": "gcp"},
)
class MwsWorkspacesCloudResourceContainer:
    def __init__(
        self,
        *,
        gcp: typing.Union["MwsWorkspacesCloudResourceContainerGcp", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param gcp: gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp MwsWorkspaces#gcp}
        '''
        if isinstance(gcp, dict):
            gcp = MwsWorkspacesCloudResourceContainerGcp(**gcp)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f4dd7649f251102b51dd417d15f825b3f89e98fb8c35e547df18b6ebd6a20e)
            check_type(argname="argument gcp", value=gcp, expected_type=type_hints["gcp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gcp": gcp,
        }

    @builtins.property
    def gcp(self) -> "MwsWorkspacesCloudResourceContainerGcp":
        '''gcp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp MwsWorkspaces#gcp}
        '''
        result = self._values.get("gcp")
        assert result is not None, "Required property 'gcp' is missing"
        return typing.cast("MwsWorkspacesCloudResourceContainerGcp", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesCloudResourceContainer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesCloudResourceContainerGcp",
    jsii_struct_bases=[],
    name_mapping={"project_id": "projectId"},
)
class MwsWorkspacesCloudResourceContainerGcp:
    def __init__(self, *, project_id: builtins.str) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#project_id MwsWorkspaces#project_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3ce8892d9e5c5e28a9f78edc940fa2ea7964137e353b0c89371852d6868a49)
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_id": project_id,
        }

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#project_id MwsWorkspaces#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesCloudResourceContainerGcp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesCloudResourceContainerGcpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesCloudResourceContainerGcpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3a5f4aa856b07ce08bf702e1f5a5dc1da58b9af3896edd326a5191a979810e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aa97a4dd3855bd2df67053994d24ff5a3f649abff800e0acfccc8541cf3ab72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesCloudResourceContainerGcp]:
        return typing.cast(typing.Optional[MwsWorkspacesCloudResourceContainerGcp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsWorkspacesCloudResourceContainerGcp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97819ae61cfa7df1274817895ddedd2a5c9546768b9fc101bc2189a1f9d4c03f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsWorkspacesCloudResourceContainerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesCloudResourceContainerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a13827c3bbc8d72468e9816dc03ecfaeb1c84cdeab67a93a430923bf689aa056)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putGcp")
    def put_gcp(self, *, project_id: builtins.str) -> None:
        '''
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#project_id MwsWorkspaces#project_id}.
        '''
        value = MwsWorkspacesCloudResourceContainerGcp(project_id=project_id)

        return typing.cast(None, jsii.invoke(self, "putGcp", [value]))

    @builtins.property
    @jsii.member(jsii_name="gcp")
    def gcp(self) -> MwsWorkspacesCloudResourceContainerGcpOutputReference:
        return typing.cast(MwsWorkspacesCloudResourceContainerGcpOutputReference, jsii.get(self, "gcp"))

    @builtins.property
    @jsii.member(jsii_name="gcpInput")
    def gcp_input(self) -> typing.Optional[MwsWorkspacesCloudResourceContainerGcp]:
        return typing.cast(typing.Optional[MwsWorkspacesCloudResourceContainerGcp], jsii.get(self, "gcpInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesCloudResourceContainer]:
        return typing.cast(typing.Optional[MwsWorkspacesCloudResourceContainer], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsWorkspacesCloudResourceContainer],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae4b02578a9a5c69e86c2395caf2dc32e29fbec747f0a9cbe320b7f9671afbc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "workspace_name": "workspaceName",
        "aws_region": "awsRegion",
        "cloud": "cloud",
        "cloud_resource_container": "cloudResourceContainer",
        "compute_mode": "computeMode",
        "creation_time": "creationTime",
        "credentials_id": "credentialsId",
        "customer_managed_key_id": "customerManagedKeyId",
        "custom_tags": "customTags",
        "deployment_name": "deploymentName",
        "external_customer_info": "externalCustomerInfo",
        "gcp_managed_network_config": "gcpManagedNetworkConfig",
        "gke_config": "gkeConfig",
        "id": "id",
        "is_no_public_ip_enabled": "isNoPublicIpEnabled",
        "location": "location",
        "managed_services_customer_managed_key_id": "managedServicesCustomerManagedKeyId",
        "network_id": "networkId",
        "pricing_tier": "pricingTier",
        "private_access_settings_id": "privateAccessSettingsId",
        "storage_configuration_id": "storageConfigurationId",
        "storage_customer_managed_key_id": "storageCustomerManagedKeyId",
        "timeouts": "timeouts",
        "token": "token",
        "workspace_id": "workspaceId",
        "workspace_status": "workspaceStatus",
        "workspace_status_message": "workspaceStatusMessage",
        "workspace_url": "workspaceUrl",
    },
)
class MwsWorkspacesConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: builtins.str,
        workspace_name: builtins.str,
        aws_region: typing.Optional[builtins.str] = None,
        cloud: typing.Optional[builtins.str] = None,
        cloud_resource_container: typing.Optional[typing.Union[MwsWorkspacesCloudResourceContainer, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_mode: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        credentials_id: typing.Optional[builtins.str] = None,
        customer_managed_key_id: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        deployment_name: typing.Optional[builtins.str] = None,
        external_customer_info: typing.Optional[typing.Union["MwsWorkspacesExternalCustomerInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_managed_network_config: typing.Optional[typing.Union["MwsWorkspacesGcpManagedNetworkConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        gke_config: typing.Optional[typing.Union["MwsWorkspacesGkeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        is_no_public_ip_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        location: typing.Optional[builtins.str] = None,
        managed_services_customer_managed_key_id: typing.Optional[builtins.str] = None,
        network_id: typing.Optional[builtins.str] = None,
        pricing_tier: typing.Optional[builtins.str] = None,
        private_access_settings_id: typing.Optional[builtins.str] = None,
        storage_configuration_id: typing.Optional[builtins.str] = None,
        storage_customer_managed_key_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["MwsWorkspacesTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        token: typing.Optional[typing.Union["MwsWorkspacesToken", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[jsii.Number] = None,
        workspace_status: typing.Optional[builtins.str] = None,
        workspace_status_message: typing.Optional[builtins.str] = None,
        workspace_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#account_id MwsWorkspaces#account_id}.
        :param workspace_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_name MwsWorkspaces#workspace_name}.
        :param aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#aws_region MwsWorkspaces#aws_region}.
        :param cloud: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud MwsWorkspaces#cloud}.
        :param cloud_resource_container: cloud_resource_container block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud_resource_container MwsWorkspaces#cloud_resource_container}
        :param compute_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#compute_mode MwsWorkspaces#compute_mode}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#creation_time MwsWorkspaces#creation_time}.
        :param credentials_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#credentials_id MwsWorkspaces#credentials_id}.
        :param customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_managed_key_id MwsWorkspaces#customer_managed_key_id}.
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#custom_tags MwsWorkspaces#custom_tags}.
        :param deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#deployment_name MwsWorkspaces#deployment_name}.
        :param external_customer_info: external_customer_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#external_customer_info MwsWorkspaces#external_customer_info}
        :param gcp_managed_network_config: gcp_managed_network_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp_managed_network_config MwsWorkspaces#gcp_managed_network_config}
        :param gke_config: gke_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_config MwsWorkspaces#gke_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#id MwsWorkspaces#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_no_public_ip_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#is_no_public_ip_enabled MwsWorkspaces#is_no_public_ip_enabled}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#location MwsWorkspaces#location}.
        :param managed_services_customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#managed_services_customer_managed_key_id MwsWorkspaces#managed_services_customer_managed_key_id}.
        :param network_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#network_id MwsWorkspaces#network_id}.
        :param pricing_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#pricing_tier MwsWorkspaces#pricing_tier}.
        :param private_access_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#private_access_settings_id MwsWorkspaces#private_access_settings_id}.
        :param storage_configuration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_configuration_id MwsWorkspaces#storage_configuration_id}.
        :param storage_customer_managed_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_customer_managed_key_id MwsWorkspaces#storage_customer_managed_key_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#timeouts MwsWorkspaces#timeouts}
        :param token: token block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token MwsWorkspaces#token}
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_id MwsWorkspaces#workspace_id}.
        :param workspace_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status MwsWorkspaces#workspace_status}.
        :param workspace_status_message: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status_message MwsWorkspaces#workspace_status_message}.
        :param workspace_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_url MwsWorkspaces#workspace_url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cloud_resource_container, dict):
            cloud_resource_container = MwsWorkspacesCloudResourceContainer(**cloud_resource_container)
        if isinstance(external_customer_info, dict):
            external_customer_info = MwsWorkspacesExternalCustomerInfo(**external_customer_info)
        if isinstance(gcp_managed_network_config, dict):
            gcp_managed_network_config = MwsWorkspacesGcpManagedNetworkConfig(**gcp_managed_network_config)
        if isinstance(gke_config, dict):
            gke_config = MwsWorkspacesGkeConfig(**gke_config)
        if isinstance(timeouts, dict):
            timeouts = MwsWorkspacesTimeouts(**timeouts)
        if isinstance(token, dict):
            token = MwsWorkspacesToken(**token)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c9cb066ba925c6799355ef28186472d153a6a22bda9822a0a07702d0f4bb6d6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument workspace_name", value=workspace_name, expected_type=type_hints["workspace_name"])
            check_type(argname="argument aws_region", value=aws_region, expected_type=type_hints["aws_region"])
            check_type(argname="argument cloud", value=cloud, expected_type=type_hints["cloud"])
            check_type(argname="argument cloud_resource_container", value=cloud_resource_container, expected_type=type_hints["cloud_resource_container"])
            check_type(argname="argument compute_mode", value=compute_mode, expected_type=type_hints["compute_mode"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument credentials_id", value=credentials_id, expected_type=type_hints["credentials_id"])
            check_type(argname="argument customer_managed_key_id", value=customer_managed_key_id, expected_type=type_hints["customer_managed_key_id"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument deployment_name", value=deployment_name, expected_type=type_hints["deployment_name"])
            check_type(argname="argument external_customer_info", value=external_customer_info, expected_type=type_hints["external_customer_info"])
            check_type(argname="argument gcp_managed_network_config", value=gcp_managed_network_config, expected_type=type_hints["gcp_managed_network_config"])
            check_type(argname="argument gke_config", value=gke_config, expected_type=type_hints["gke_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument is_no_public_ip_enabled", value=is_no_public_ip_enabled, expected_type=type_hints["is_no_public_ip_enabled"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument managed_services_customer_managed_key_id", value=managed_services_customer_managed_key_id, expected_type=type_hints["managed_services_customer_managed_key_id"])
            check_type(argname="argument network_id", value=network_id, expected_type=type_hints["network_id"])
            check_type(argname="argument pricing_tier", value=pricing_tier, expected_type=type_hints["pricing_tier"])
            check_type(argname="argument private_access_settings_id", value=private_access_settings_id, expected_type=type_hints["private_access_settings_id"])
            check_type(argname="argument storage_configuration_id", value=storage_configuration_id, expected_type=type_hints["storage_configuration_id"])
            check_type(argname="argument storage_customer_managed_key_id", value=storage_customer_managed_key_id, expected_type=type_hints["storage_customer_managed_key_id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
            check_type(argname="argument workspace_status", value=workspace_status, expected_type=type_hints["workspace_status"])
            check_type(argname="argument workspace_status_message", value=workspace_status_message, expected_type=type_hints["workspace_status_message"])
            check_type(argname="argument workspace_url", value=workspace_url, expected_type=type_hints["workspace_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "workspace_name": workspace_name,
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
        if aws_region is not None:
            self._values["aws_region"] = aws_region
        if cloud is not None:
            self._values["cloud"] = cloud
        if cloud_resource_container is not None:
            self._values["cloud_resource_container"] = cloud_resource_container
        if compute_mode is not None:
            self._values["compute_mode"] = compute_mode
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if credentials_id is not None:
            self._values["credentials_id"] = credentials_id
        if customer_managed_key_id is not None:
            self._values["customer_managed_key_id"] = customer_managed_key_id
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if deployment_name is not None:
            self._values["deployment_name"] = deployment_name
        if external_customer_info is not None:
            self._values["external_customer_info"] = external_customer_info
        if gcp_managed_network_config is not None:
            self._values["gcp_managed_network_config"] = gcp_managed_network_config
        if gke_config is not None:
            self._values["gke_config"] = gke_config
        if id is not None:
            self._values["id"] = id
        if is_no_public_ip_enabled is not None:
            self._values["is_no_public_ip_enabled"] = is_no_public_ip_enabled
        if location is not None:
            self._values["location"] = location
        if managed_services_customer_managed_key_id is not None:
            self._values["managed_services_customer_managed_key_id"] = managed_services_customer_managed_key_id
        if network_id is not None:
            self._values["network_id"] = network_id
        if pricing_tier is not None:
            self._values["pricing_tier"] = pricing_tier
        if private_access_settings_id is not None:
            self._values["private_access_settings_id"] = private_access_settings_id
        if storage_configuration_id is not None:
            self._values["storage_configuration_id"] = storage_configuration_id
        if storage_customer_managed_key_id is not None:
            self._values["storage_customer_managed_key_id"] = storage_customer_managed_key_id
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if token is not None:
            self._values["token"] = token
        if workspace_id is not None:
            self._values["workspace_id"] = workspace_id
        if workspace_status is not None:
            self._values["workspace_status"] = workspace_status
        if workspace_status_message is not None:
            self._values["workspace_status_message"] = workspace_status_message
        if workspace_url is not None:
            self._values["workspace_url"] = workspace_url

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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#account_id MwsWorkspaces#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_name MwsWorkspaces#workspace_name}.'''
        result = self._values.get("workspace_name")
        assert result is not None, "Required property 'workspace_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#aws_region MwsWorkspaces#aws_region}.'''
        result = self._values.get("aws_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud MwsWorkspaces#cloud}.'''
        result = self._values.get("cloud")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_resource_container(
        self,
    ) -> typing.Optional[MwsWorkspacesCloudResourceContainer]:
        '''cloud_resource_container block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#cloud_resource_container MwsWorkspaces#cloud_resource_container}
        '''
        result = self._values.get("cloud_resource_container")
        return typing.cast(typing.Optional[MwsWorkspacesCloudResourceContainer], result)

    @builtins.property
    def compute_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#compute_mode MwsWorkspaces#compute_mode}.'''
        result = self._values.get("compute_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#creation_time MwsWorkspaces#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def credentials_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#credentials_id MwsWorkspaces#credentials_id}.'''
        result = self._values.get("credentials_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_managed_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_managed_key_id MwsWorkspaces#customer_managed_key_id}.'''
        result = self._values.get("customer_managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#custom_tags MwsWorkspaces#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def deployment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#deployment_name MwsWorkspaces#deployment_name}.'''
        result = self._values.get("deployment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_customer_info(
        self,
    ) -> typing.Optional["MwsWorkspacesExternalCustomerInfo"]:
        '''external_customer_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#external_customer_info MwsWorkspaces#external_customer_info}
        '''
        result = self._values.get("external_customer_info")
        return typing.cast(typing.Optional["MwsWorkspacesExternalCustomerInfo"], result)

    @builtins.property
    def gcp_managed_network_config(
        self,
    ) -> typing.Optional["MwsWorkspacesGcpManagedNetworkConfig"]:
        '''gcp_managed_network_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gcp_managed_network_config MwsWorkspaces#gcp_managed_network_config}
        '''
        result = self._values.get("gcp_managed_network_config")
        return typing.cast(typing.Optional["MwsWorkspacesGcpManagedNetworkConfig"], result)

    @builtins.property
    def gke_config(self) -> typing.Optional["MwsWorkspacesGkeConfig"]:
        '''gke_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_config MwsWorkspaces#gke_config}
        '''
        result = self._values.get("gke_config")
        return typing.cast(typing.Optional["MwsWorkspacesGkeConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#id MwsWorkspaces#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_no_public_ip_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#is_no_public_ip_enabled MwsWorkspaces#is_no_public_ip_enabled}.'''
        result = self._values.get("is_no_public_ip_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#location MwsWorkspaces#location}.'''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_services_customer_managed_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#managed_services_customer_managed_key_id MwsWorkspaces#managed_services_customer_managed_key_id}.'''
        result = self._values.get("managed_services_customer_managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#network_id MwsWorkspaces#network_id}.'''
        result = self._values.get("network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pricing_tier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#pricing_tier MwsWorkspaces#pricing_tier}.'''
        result = self._values.get("pricing_tier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_access_settings_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#private_access_settings_id MwsWorkspaces#private_access_settings_id}.'''
        result = self._values.get("private_access_settings_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_configuration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_configuration_id MwsWorkspaces#storage_configuration_id}.'''
        result = self._values.get("storage_configuration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_customer_managed_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#storage_customer_managed_key_id MwsWorkspaces#storage_customer_managed_key_id}.'''
        result = self._values.get("storage_customer_managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MwsWorkspacesTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#timeouts MwsWorkspaces#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MwsWorkspacesTimeouts"], result)

    @builtins.property
    def token(self) -> typing.Optional["MwsWorkspacesToken"]:
        '''token block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token MwsWorkspaces#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional["MwsWorkspacesToken"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_id MwsWorkspaces#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def workspace_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status MwsWorkspaces#workspace_status}.'''
        result = self._values.get("workspace_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_status_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_status_message MwsWorkspaces#workspace_status_message}.'''
        result = self._values.get("workspace_status_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#workspace_url MwsWorkspaces#workspace_url}.'''
        result = self._values.get("workspace_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesExternalCustomerInfo",
    jsii_struct_bases=[],
    name_mapping={
        "authoritative_user_email": "authoritativeUserEmail",
        "authoritative_user_full_name": "authoritativeUserFullName",
        "customer_name": "customerName",
    },
)
class MwsWorkspacesExternalCustomerInfo:
    def __init__(
        self,
        *,
        authoritative_user_email: builtins.str,
        authoritative_user_full_name: builtins.str,
        customer_name: builtins.str,
    ) -> None:
        '''
        :param authoritative_user_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_email MwsWorkspaces#authoritative_user_email}.
        :param authoritative_user_full_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_full_name MwsWorkspaces#authoritative_user_full_name}.
        :param customer_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_name MwsWorkspaces#customer_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cbe57bc6b9ceab08c04aca7eabe62f846211201f1816a81670bda42aa538e8c)
            check_type(argname="argument authoritative_user_email", value=authoritative_user_email, expected_type=type_hints["authoritative_user_email"])
            check_type(argname="argument authoritative_user_full_name", value=authoritative_user_full_name, expected_type=type_hints["authoritative_user_full_name"])
            check_type(argname="argument customer_name", value=customer_name, expected_type=type_hints["customer_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authoritative_user_email": authoritative_user_email,
            "authoritative_user_full_name": authoritative_user_full_name,
            "customer_name": customer_name,
        }

    @builtins.property
    def authoritative_user_email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_email MwsWorkspaces#authoritative_user_email}.'''
        result = self._values.get("authoritative_user_email")
        assert result is not None, "Required property 'authoritative_user_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authoritative_user_full_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#authoritative_user_full_name MwsWorkspaces#authoritative_user_full_name}.'''
        result = self._values.get("authoritative_user_full_name")
        assert result is not None, "Required property 'authoritative_user_full_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def customer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#customer_name MwsWorkspaces#customer_name}.'''
        result = self._values.get("customer_name")
        assert result is not None, "Required property 'customer_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesExternalCustomerInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesExternalCustomerInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesExternalCustomerInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74b2187c739a47bf4272938f37105a5cc73d9364d6d5f83d6b1e09b7fcaeb2bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="authoritativeUserEmailInput")
    def authoritative_user_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authoritativeUserEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="authoritativeUserFullNameInput")
    def authoritative_user_full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authoritativeUserFullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="customerNameInput")
    def customer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authoritativeUserEmail")
    def authoritative_user_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authoritativeUserEmail"))

    @authoritative_user_email.setter
    def authoritative_user_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba7a0bd9e3f74e8a90a3eb770903f94b0a20e56ce7ee6df32a870757495d3bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authoritativeUserEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authoritativeUserFullName")
    def authoritative_user_full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authoritativeUserFullName"))

    @authoritative_user_full_name.setter
    def authoritative_user_full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1cf06fec6fcd0734d76d00fea016915541df78f7e70856f69942bdfd0bde5be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authoritativeUserFullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customerName")
    def customer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerName"))

    @customer_name.setter
    def customer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67798372991f947dc125837dcefbaa50468d0d6e6426cc3a4175465dbcbfd5f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesExternalCustomerInfo]:
        return typing.cast(typing.Optional[MwsWorkspacesExternalCustomerInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsWorkspacesExternalCustomerInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cfcd7d5e6bdee85b6d7e5b221e4a5372728ebc630ac6965b56f7c75457ba7ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesGcpManagedNetworkConfig",
    jsii_struct_bases=[],
    name_mapping={
        "subnet_cidr": "subnetCidr",
        "gke_cluster_pod_ip_range": "gkeClusterPodIpRange",
        "gke_cluster_service_ip_range": "gkeClusterServiceIpRange",
    },
)
class MwsWorkspacesGcpManagedNetworkConfig:
    def __init__(
        self,
        *,
        subnet_cidr: builtins.str,
        gke_cluster_pod_ip_range: typing.Optional[builtins.str] = None,
        gke_cluster_service_ip_range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param subnet_cidr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#subnet_cidr MwsWorkspaces#subnet_cidr}.
        :param gke_cluster_pod_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_pod_ip_range MwsWorkspaces#gke_cluster_pod_ip_range}.
        :param gke_cluster_service_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_service_ip_range MwsWorkspaces#gke_cluster_service_ip_range}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56755b41293d08b4f3557e1f100f93ffae3d9b07e46a61a6e988fde7100f142b)
            check_type(argname="argument subnet_cidr", value=subnet_cidr, expected_type=type_hints["subnet_cidr"])
            check_type(argname="argument gke_cluster_pod_ip_range", value=gke_cluster_pod_ip_range, expected_type=type_hints["gke_cluster_pod_ip_range"])
            check_type(argname="argument gke_cluster_service_ip_range", value=gke_cluster_service_ip_range, expected_type=type_hints["gke_cluster_service_ip_range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subnet_cidr": subnet_cidr,
        }
        if gke_cluster_pod_ip_range is not None:
            self._values["gke_cluster_pod_ip_range"] = gke_cluster_pod_ip_range
        if gke_cluster_service_ip_range is not None:
            self._values["gke_cluster_service_ip_range"] = gke_cluster_service_ip_range

    @builtins.property
    def subnet_cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#subnet_cidr MwsWorkspaces#subnet_cidr}.'''
        result = self._values.get("subnet_cidr")
        assert result is not None, "Required property 'subnet_cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gke_cluster_pod_ip_range(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_pod_ip_range MwsWorkspaces#gke_cluster_pod_ip_range}.'''
        result = self._values.get("gke_cluster_pod_ip_range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_service_ip_range(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#gke_cluster_service_ip_range MwsWorkspaces#gke_cluster_service_ip_range}.'''
        result = self._values.get("gke_cluster_service_ip_range")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesGcpManagedNetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesGcpManagedNetworkConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesGcpManagedNetworkConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8071d65d97747ba40c633dbf2fbb2d8a059d6e2b5e16395068c2c89449a3ac78)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGkeClusterPodIpRange")
    def reset_gke_cluster_pod_ip_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeClusterPodIpRange", []))

    @jsii.member(jsii_name="resetGkeClusterServiceIpRange")
    def reset_gke_cluster_service_ip_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeClusterServiceIpRange", []))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterPodIpRangeInput")
    def gke_cluster_pod_ip_range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeClusterPodIpRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterServiceIpRangeInput")
    def gke_cluster_service_ip_range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeClusterServiceIpRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetCidrInput")
    def subnet_cidr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterPodIpRange")
    def gke_cluster_pod_ip_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterPodIpRange"))

    @gke_cluster_pod_ip_range.setter
    def gke_cluster_pod_ip_range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17b18a51a2d9d59099bbec75fb6aa89f434d1349001d5d00f5c8f816b1789d75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterPodIpRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gkeClusterServiceIpRange")
    def gke_cluster_service_ip_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterServiceIpRange"))

    @gke_cluster_service_ip_range.setter
    def gke_cluster_service_ip_range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c1d109f2f7a086209b86b2e3de7963c8d7a282faca5cf3ce738b1f57350fc29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterServiceIpRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetCidr")
    def subnet_cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetCidr"))

    @subnet_cidr.setter
    def subnet_cidr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6041da0a72360281d33005dc0089f706c55b02d62635ceefcf0446b85b1d5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetCidr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesGcpManagedNetworkConfig]:
        return typing.cast(typing.Optional[MwsWorkspacesGcpManagedNetworkConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsWorkspacesGcpManagedNetworkConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f18ad3310cb61ca298de7e75d924291a5cf1e309ac3fb6a19b345b520b3159e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesGkeConfig",
    jsii_struct_bases=[],
    name_mapping={
        "connectivity_type": "connectivityType",
        "master_ip_range": "masterIpRange",
    },
)
class MwsWorkspacesGkeConfig:
    def __init__(
        self,
        *,
        connectivity_type: typing.Optional[builtins.str] = None,
        master_ip_range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connectivity_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#connectivity_type MwsWorkspaces#connectivity_type}.
        :param master_ip_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#master_ip_range MwsWorkspaces#master_ip_range}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86a79dba50b85e428b5f402858c0e3260bf315cddd80056efd6a9cae40664903)
            check_type(argname="argument connectivity_type", value=connectivity_type, expected_type=type_hints["connectivity_type"])
            check_type(argname="argument master_ip_range", value=master_ip_range, expected_type=type_hints["master_ip_range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connectivity_type is not None:
            self._values["connectivity_type"] = connectivity_type
        if master_ip_range is not None:
            self._values["master_ip_range"] = master_ip_range

    @builtins.property
    def connectivity_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#connectivity_type MwsWorkspaces#connectivity_type}.'''
        result = self._values.get("connectivity_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_ip_range(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#master_ip_range MwsWorkspaces#master_ip_range}.'''
        result = self._values.get("master_ip_range")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesGkeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesGkeConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesGkeConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__efb0234eb4e7212829aaefcc3f942a13ae5f153b6ca09fde1e291ee0bab19366)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectivityType")
    def reset_connectivity_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectivityType", []))

    @jsii.member(jsii_name="resetMasterIpRange")
    def reset_master_ip_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterIpRange", []))

    @builtins.property
    @jsii.member(jsii_name="connectivityTypeInput")
    def connectivity_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectivityTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="masterIpRangeInput")
    def master_ip_range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterIpRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectivityType")
    def connectivity_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectivityType"))

    @connectivity_type.setter
    def connectivity_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fa96b10a3fab6497cdc8474db21a474d3f434e6bcf102201e45bc7941afbc5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectivityType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterIpRange")
    def master_ip_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterIpRange"))

    @master_ip_range.setter
    def master_ip_range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1467f6f039432477b300f2ef65506fbdfd59424ac312d869e874a458bf9c7139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterIpRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesGkeConfig]:
        return typing.cast(typing.Optional[MwsWorkspacesGkeConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MwsWorkspacesGkeConfig]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7c276bb13b41cedb580947aaf49af35d889468937cc9458ad0d99c0894db73b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "read": "read", "update": "update"},
)
class MwsWorkspacesTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#create MwsWorkspaces#create}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#read MwsWorkspaces#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#update MwsWorkspaces#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f5d34d3420b5ffd039601616838e8272b0d5aff8576caecf5a636cb02394f3)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if read is not None:
            self._values["read"] = read
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#create MwsWorkspaces#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#read MwsWorkspaces#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#update MwsWorkspaces#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc8ff9f7fbc9dfa543c351f97dce91463cd1652a2b37b0505811a4d5381c6d2f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7392b0f138d34a3b7b521a30414fd7fe2a68a3b3a59a2bbe9f9811e1e4c3fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43d2cd4fc4150d63094559701c71206cfaec244a6049975f1785e1e73d60fa81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07b344a8d63a55656552bfeef7c7cc081697288ab857e04ed01bbf0dcfe2967c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsWorkspacesTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsWorkspacesTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsWorkspacesTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acf486d3652a92fbfe1a2fc12b8fe7e47603343d8b8a08f9732cd86e81b5dcd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesToken",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "lifetime_seconds": "lifetimeSeconds",
        "token_id": "tokenId",
        "token_value": "tokenValue",
    },
)
class MwsWorkspacesToken:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        lifetime_seconds: typing.Optional[jsii.Number] = None,
        token_id: typing.Optional[builtins.str] = None,
        token_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#comment MwsWorkspaces#comment}.
        :param lifetime_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#lifetime_seconds MwsWorkspaces#lifetime_seconds}.
        :param token_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_id MwsWorkspaces#token_id}.
        :param token_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_value MwsWorkspaces#token_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8201105f41bec400c3b0650cf63e8a511b5e2460fa4086587abdab63bc867410)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument lifetime_seconds", value=lifetime_seconds, expected_type=type_hints["lifetime_seconds"])
            check_type(argname="argument token_id", value=token_id, expected_type=type_hints["token_id"])
            check_type(argname="argument token_value", value=token_value, expected_type=type_hints["token_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if lifetime_seconds is not None:
            self._values["lifetime_seconds"] = lifetime_seconds
        if token_id is not None:
            self._values["token_id"] = token_id
        if token_value is not None:
            self._values["token_value"] = token_value

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#comment MwsWorkspaces#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifetime_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#lifetime_seconds MwsWorkspaces#lifetime_seconds}.'''
        result = self._values.get("lifetime_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_id MwsWorkspaces#token_id}.'''
        result = self._values.get("token_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_workspaces#token_value MwsWorkspaces#token_value}.'''
        result = self._values.get("token_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsWorkspacesToken(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsWorkspacesTokenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsWorkspaces.MwsWorkspacesTokenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__409ddc34fd6fce1ee4f945985b934b1f54b4f2774a98bd79fc2766a0a430f310)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetLifetimeSeconds")
    def reset_lifetime_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifetimeSeconds", []))

    @jsii.member(jsii_name="resetTokenId")
    def reset_token_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenId", []))

    @jsii.member(jsii_name="resetTokenValue")
    def reset_token_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenValue", []))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="lifetimeSecondsInput")
    def lifetime_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lifetimeSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenIdInput")
    def token_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenValueInput")
    def token_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenValueInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf52e4c10797da40d821b53ebc1b94cd7de184fbeccd3a5825f42f2a09572d0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lifetimeSeconds")
    def lifetime_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lifetimeSeconds"))

    @lifetime_seconds.setter
    def lifetime_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__595b340830266ca236cc7a47a9ad8e09555e04644aa465d9207458af95081319)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lifetimeSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenId")
    def token_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenId"))

    @token_id.setter
    def token_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25acf899dd6a1320b801ff94d6a08ce448f4594cd4d85e84b0b8d545b7dd05af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenValue")
    def token_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenValue"))

    @token_value.setter
    def token_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__106d5e21951d86b1ab6c6fe307e5d4d886cd9b35f334d075869fc44dcf44a380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsWorkspacesToken]:
        return typing.cast(typing.Optional[MwsWorkspacesToken], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MwsWorkspacesToken]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__788391a9128a8e157779cd762c534127fe5817817cd9ec215ba6fefa62337141)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MwsWorkspaces",
    "MwsWorkspacesCloudResourceContainer",
    "MwsWorkspacesCloudResourceContainerGcp",
    "MwsWorkspacesCloudResourceContainerGcpOutputReference",
    "MwsWorkspacesCloudResourceContainerOutputReference",
    "MwsWorkspacesConfig",
    "MwsWorkspacesExternalCustomerInfo",
    "MwsWorkspacesExternalCustomerInfoOutputReference",
    "MwsWorkspacesGcpManagedNetworkConfig",
    "MwsWorkspacesGcpManagedNetworkConfigOutputReference",
    "MwsWorkspacesGkeConfig",
    "MwsWorkspacesGkeConfigOutputReference",
    "MwsWorkspacesTimeouts",
    "MwsWorkspacesTimeoutsOutputReference",
    "MwsWorkspacesToken",
    "MwsWorkspacesTokenOutputReference",
]

publication.publish()

def _typecheckingstub__680d70784fa634cc71a9b01783e55bf3033a623db00c67733876b2e9afaf47c6(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: builtins.str,
    workspace_name: builtins.str,
    aws_region: typing.Optional[builtins.str] = None,
    cloud: typing.Optional[builtins.str] = None,
    cloud_resource_container: typing.Optional[typing.Union[MwsWorkspacesCloudResourceContainer, typing.Dict[builtins.str, typing.Any]]] = None,
    compute_mode: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    credentials_id: typing.Optional[builtins.str] = None,
    customer_managed_key_id: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    deployment_name: typing.Optional[builtins.str] = None,
    external_customer_info: typing.Optional[typing.Union[MwsWorkspacesExternalCustomerInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_managed_network_config: typing.Optional[typing.Union[MwsWorkspacesGcpManagedNetworkConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    gke_config: typing.Optional[typing.Union[MwsWorkspacesGkeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    is_no_public_ip_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    location: typing.Optional[builtins.str] = None,
    managed_services_customer_managed_key_id: typing.Optional[builtins.str] = None,
    network_id: typing.Optional[builtins.str] = None,
    pricing_tier: typing.Optional[builtins.str] = None,
    private_access_settings_id: typing.Optional[builtins.str] = None,
    storage_configuration_id: typing.Optional[builtins.str] = None,
    storage_customer_managed_key_id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[MwsWorkspacesTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    token: typing.Optional[typing.Union[MwsWorkspacesToken, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[jsii.Number] = None,
    workspace_status: typing.Optional[builtins.str] = None,
    workspace_status_message: typing.Optional[builtins.str] = None,
    workspace_url: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__518bc06e0416f074d4a3dac70d4d25963991149f96d1bbce4c5031b215201f4c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05183b470223f1a801c482043e79dd1a7f20cd172aa38f610a28f8aeadcfd0a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43363e860473b0ea079f454bd682c51f6036c3dc8d131b5eac24e20779d80b83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d790cdd80ed5b547b7136dc048410b42785e63b739eb310a1e8633fd5f9220e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f989d6d4bc310dc6ee02488d35b48d2d42080ec12a247cc375d05af9e9bcf504(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edf7ae8f7248363260e62dd0aa468cc88bdcf49f49a56c3f8575cd57abb92340(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fccfe5f88c439d8057e3b68b42ec727fb0a9555904367175b039be8bd1c82bf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9777a9f463fc23d1828441a45ce8551a356bb6b28bcdc6b280cfa64fab8e41b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99367dddc1bcf9ce97a51e6dad244cd827c2312e00c7cd36ecebcf5198866ba5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62115814f39c6a532d25455633af7d2300b6fc004a45d67006670d0d15491968(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bd705e61f79ad72732eac80b5a9ad658b13cd2dadb54107b67f79fe2dfa733(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b44147a5403101b5b43749310d5ab8dc27ece8a093f473cf0821686803051b7c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fa84e5fd85d03f597c44a7eeb742ba52afd72d37c5f876120666053d77d73d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__756262a9c3dc18683c02cdc7ae492bd506b7cb597f61ed90f6128100b1b2416f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70be8c2387d3570faa221e02a3c2325a65d5fac4d2632d0fae801a9f06b09a54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa3e99839f82c11f84f0c1de18d9bf17431eeffb61ed503bf65fa33b372f06af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd2462b71c0bb53845489d06e5951b4de783880d950c9ef2d9cd45ed7b654dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb1a300332b5f79f343d38d36175bab1a24d1b1325dfdc773ad27a88dd455b64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9449fecc23d22668ccb3ea512166b1248dfa37eb9a348edaba0c70b06ca733b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2544f921304b6aebf0c445e8883969a247b7119712590602bac474c902f3adb4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e67996777048ad9adf8e32c192cc825f51904368b951e226f7c5ec7a15a86911(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdfca99cf8bce327fc8f51ff9cccaa31ddeff31421286cce7f01bdaa0f3de3dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f86fa9eb18a18969407c0c6e73fdd21b8033835c66f58053b280bae46c06105(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a86ecdbb85a4feacc361296916c0190e4e5954800e7fc4a0717bde53e69cd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f4dd7649f251102b51dd417d15f825b3f89e98fb8c35e547df18b6ebd6a20e(
    *,
    gcp: typing.Union[MwsWorkspacesCloudResourceContainerGcp, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3ce8892d9e5c5e28a9f78edc940fa2ea7964137e353b0c89371852d6868a49(
    *,
    project_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3a5f4aa856b07ce08bf702e1f5a5dc1da58b9af3896edd326a5191a979810e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aa97a4dd3855bd2df67053994d24ff5a3f649abff800e0acfccc8541cf3ab72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97819ae61cfa7df1274817895ddedd2a5c9546768b9fc101bc2189a1f9d4c03f(
    value: typing.Optional[MwsWorkspacesCloudResourceContainerGcp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a13827c3bbc8d72468e9816dc03ecfaeb1c84cdeab67a93a430923bf689aa056(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae4b02578a9a5c69e86c2395caf2dc32e29fbec747f0a9cbe320b7f9671afbc2(
    value: typing.Optional[MwsWorkspacesCloudResourceContainer],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c9cb066ba925c6799355ef28186472d153a6a22bda9822a0a07702d0f4bb6d6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    workspace_name: builtins.str,
    aws_region: typing.Optional[builtins.str] = None,
    cloud: typing.Optional[builtins.str] = None,
    cloud_resource_container: typing.Optional[typing.Union[MwsWorkspacesCloudResourceContainer, typing.Dict[builtins.str, typing.Any]]] = None,
    compute_mode: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    credentials_id: typing.Optional[builtins.str] = None,
    customer_managed_key_id: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    deployment_name: typing.Optional[builtins.str] = None,
    external_customer_info: typing.Optional[typing.Union[MwsWorkspacesExternalCustomerInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_managed_network_config: typing.Optional[typing.Union[MwsWorkspacesGcpManagedNetworkConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    gke_config: typing.Optional[typing.Union[MwsWorkspacesGkeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    is_no_public_ip_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    location: typing.Optional[builtins.str] = None,
    managed_services_customer_managed_key_id: typing.Optional[builtins.str] = None,
    network_id: typing.Optional[builtins.str] = None,
    pricing_tier: typing.Optional[builtins.str] = None,
    private_access_settings_id: typing.Optional[builtins.str] = None,
    storage_configuration_id: typing.Optional[builtins.str] = None,
    storage_customer_managed_key_id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[MwsWorkspacesTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    token: typing.Optional[typing.Union[MwsWorkspacesToken, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[jsii.Number] = None,
    workspace_status: typing.Optional[builtins.str] = None,
    workspace_status_message: typing.Optional[builtins.str] = None,
    workspace_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbe57bc6b9ceab08c04aca7eabe62f846211201f1816a81670bda42aa538e8c(
    *,
    authoritative_user_email: builtins.str,
    authoritative_user_full_name: builtins.str,
    customer_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b2187c739a47bf4272938f37105a5cc73d9364d6d5f83d6b1e09b7fcaeb2bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba7a0bd9e3f74e8a90a3eb770903f94b0a20e56ce7ee6df32a870757495d3bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1cf06fec6fcd0734d76d00fea016915541df78f7e70856f69942bdfd0bde5be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67798372991f947dc125837dcefbaa50468d0d6e6426cc3a4175465dbcbfd5f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cfcd7d5e6bdee85b6d7e5b221e4a5372728ebc630ac6965b56f7c75457ba7ef(
    value: typing.Optional[MwsWorkspacesExternalCustomerInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56755b41293d08b4f3557e1f100f93ffae3d9b07e46a61a6e988fde7100f142b(
    *,
    subnet_cidr: builtins.str,
    gke_cluster_pod_ip_range: typing.Optional[builtins.str] = None,
    gke_cluster_service_ip_range: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8071d65d97747ba40c633dbf2fbb2d8a059d6e2b5e16395068c2c89449a3ac78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17b18a51a2d9d59099bbec75fb6aa89f434d1349001d5d00f5c8f816b1789d75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c1d109f2f7a086209b86b2e3de7963c8d7a282faca5cf3ce738b1f57350fc29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6041da0a72360281d33005dc0089f706c55b02d62635ceefcf0446b85b1d5dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f18ad3310cb61ca298de7e75d924291a5cf1e309ac3fb6a19b345b520b3159e(
    value: typing.Optional[MwsWorkspacesGcpManagedNetworkConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86a79dba50b85e428b5f402858c0e3260bf315cddd80056efd6a9cae40664903(
    *,
    connectivity_type: typing.Optional[builtins.str] = None,
    master_ip_range: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb0234eb4e7212829aaefcc3f942a13ae5f153b6ca09fde1e291ee0bab19366(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa96b10a3fab6497cdc8474db21a474d3f434e6bcf102201e45bc7941afbc5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1467f6f039432477b300f2ef65506fbdfd59424ac312d869e874a458bf9c7139(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7c276bb13b41cedb580947aaf49af35d889468937cc9458ad0d99c0894db73b(
    value: typing.Optional[MwsWorkspacesGkeConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f5d34d3420b5ffd039601616838e8272b0d5aff8576caecf5a636cb02394f3(
    *,
    create: typing.Optional[builtins.str] = None,
    read: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc8ff9f7fbc9dfa543c351f97dce91463cd1652a2b37b0505811a4d5381c6d2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7392b0f138d34a3b7b521a30414fd7fe2a68a3b3a59a2bbe9f9811e1e4c3fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43d2cd4fc4150d63094559701c71206cfaec244a6049975f1785e1e73d60fa81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07b344a8d63a55656552bfeef7c7cc081697288ab857e04ed01bbf0dcfe2967c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acf486d3652a92fbfe1a2fc12b8fe7e47603343d8b8a08f9732cd86e81b5dcd3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsWorkspacesTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8201105f41bec400c3b0650cf63e8a511b5e2460fa4086587abdab63bc867410(
    *,
    comment: typing.Optional[builtins.str] = None,
    lifetime_seconds: typing.Optional[jsii.Number] = None,
    token_id: typing.Optional[builtins.str] = None,
    token_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409ddc34fd6fce1ee4f945985b934b1f54b4f2774a98bd79fc2766a0a430f310(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf52e4c10797da40d821b53ebc1b94cd7de184fbeccd3a5825f42f2a09572d0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595b340830266ca236cc7a47a9ad8e09555e04644aa465d9207458af95081319(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25acf899dd6a1320b801ff94d6a08ce448f4594cd4d85e84b0b8d545b7dd05af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__106d5e21951d86b1ab6c6fe307e5d4d886cd9b35f334d075869fc44dcf44a380(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__788391a9128a8e157779cd762c534127fe5817817cd9ec215ba6fefa62337141(
    value: typing.Optional[MwsWorkspacesToken],
) -> None:
    """Type checking stubs"""
    pass
