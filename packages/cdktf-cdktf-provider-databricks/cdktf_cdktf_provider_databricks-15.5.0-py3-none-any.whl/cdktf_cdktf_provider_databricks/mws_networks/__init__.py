r'''
# `databricks_mws_networks`

Refer to the Terraform Registry for docs: [`databricks_mws_networks`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks).
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


class MwsNetworks(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworks",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks databricks_mws_networks}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: builtins.str,
        network_name: builtins.str,
        creation_time: typing.Optional[jsii.Number] = None,
        error_messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworksErrorMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_network_info: typing.Optional[typing.Union["MwsNetworksGcpNetworkInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoints: typing.Optional[typing.Union["MwsNetworksVpcEndpoints", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        vpc_status: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks databricks_mws_networks} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#account_id MwsNetworks#account_id}.
        :param network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_name MwsNetworks#network_name}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#creation_time MwsNetworks#creation_time}.
        :param error_messages: error_messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_messages MwsNetworks#error_messages}
        :param gcp_network_info: gcp_network_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#gcp_network_info MwsNetworks#gcp_network_info}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#id MwsNetworks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_id MwsNetworks#network_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#security_group_ids MwsNetworks#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_ids MwsNetworks#subnet_ids}.
        :param vpc_endpoints: vpc_endpoints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_endpoints MwsNetworks#vpc_endpoints}
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.
        :param vpc_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_status MwsNetworks#vpc_status}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#workspace_id MwsNetworks#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b6a07da38e683c274d1086738200902b979f438cc6e2ae7545a68654459943d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MwsNetworksConfig(
            account_id=account_id,
            network_name=network_name,
            creation_time=creation_time,
            error_messages=error_messages,
            gcp_network_info=gcp_network_info,
            id=id,
            network_id=network_id,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            vpc_endpoints=vpc_endpoints,
            vpc_id=vpc_id,
            vpc_status=vpc_status,
            workspace_id=workspace_id,
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
        '''Generates CDKTF code for importing a MwsNetworks resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MwsNetworks to import.
        :param import_from_id: The id of the existing MwsNetworks that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MwsNetworks to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef34f4626636f0288f8a45055bef65a3e78d81aabbe2c88e878a403d875a15b5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putErrorMessages")
    def put_error_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworksErrorMessages", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ffe74c25a3df5bdcc9c113c32d17ed1a98fa6e04ebcaafab53ea41d8f5f92bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putErrorMessages", [value]))

    @jsii.member(jsii_name="putGcpNetworkInfo")
    def put_gcp_network_info(
        self,
        *,
        network_project_id: builtins.str,
        subnet_id: builtins.str,
        subnet_region: builtins.str,
        vpc_id: builtins.str,
        pod_ip_range_name: typing.Optional[builtins.str] = None,
        service_ip_range_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param network_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_project_id MwsNetworks#network_project_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_id MwsNetworks#subnet_id}.
        :param subnet_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_region MwsNetworks#subnet_region}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.
        :param pod_ip_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#pod_ip_range_name MwsNetworks#pod_ip_range_name}.
        :param service_ip_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#service_ip_range_name MwsNetworks#service_ip_range_name}.
        '''
        value = MwsNetworksGcpNetworkInfo(
            network_project_id=network_project_id,
            subnet_id=subnet_id,
            subnet_region=subnet_region,
            vpc_id=vpc_id,
            pod_ip_range_name=pod_ip_range_name,
            service_ip_range_name=service_ip_range_name,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpNetworkInfo", [value]))

    @jsii.member(jsii_name="putVpcEndpoints")
    def put_vpc_endpoints(
        self,
        *,
        dataplane_relay: typing.Sequence[builtins.str],
        rest_api: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param dataplane_relay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#dataplane_relay MwsNetworks#dataplane_relay}.
        :param rest_api: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#rest_api MwsNetworks#rest_api}.
        '''
        value = MwsNetworksVpcEndpoints(
            dataplane_relay=dataplane_relay, rest_api=rest_api
        )

        return typing.cast(None, jsii.invoke(self, "putVpcEndpoints", [value]))

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetErrorMessages")
    def reset_error_messages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorMessages", []))

    @jsii.member(jsii_name="resetGcpNetworkInfo")
    def reset_gcp_network_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpNetworkInfo", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNetworkId")
    def reset_network_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkId", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @jsii.member(jsii_name="resetVpcEndpoints")
    def reset_vpc_endpoints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpoints", []))

    @jsii.member(jsii_name="resetVpcId")
    def reset_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcId", []))

    @jsii.member(jsii_name="resetVpcStatus")
    def reset_vpc_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcStatus", []))

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
    @jsii.member(jsii_name="errorMessages")
    def error_messages(self) -> "MwsNetworksErrorMessagesList":
        return typing.cast("MwsNetworksErrorMessagesList", jsii.get(self, "errorMessages"))

    @builtins.property
    @jsii.member(jsii_name="gcpNetworkInfo")
    def gcp_network_info(self) -> "MwsNetworksGcpNetworkInfoOutputReference":
        return typing.cast("MwsNetworksGcpNetworkInfoOutputReference", jsii.get(self, "gcpNetworkInfo"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpoints")
    def vpc_endpoints(self) -> "MwsNetworksVpcEndpointsOutputReference":
        return typing.cast("MwsNetworksVpcEndpointsOutputReference", jsii.get(self, "vpcEndpoints"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="errorMessagesInput")
    def error_messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworksErrorMessages"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworksErrorMessages"]]], jsii.get(self, "errorMessagesInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpNetworkInfoInput")
    def gcp_network_info_input(self) -> typing.Optional["MwsNetworksGcpNetworkInfo"]:
        return typing.cast(typing.Optional["MwsNetworksGcpNetworkInfo"], jsii.get(self, "gcpNetworkInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="networkIdInput")
    def network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="networkNameInput")
    def network_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkNameInput"))

    @builtins.property
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointsInput")
    def vpc_endpoints_input(self) -> typing.Optional["MwsNetworksVpcEndpoints"]:
        return typing.cast(typing.Optional["MwsNetworksVpcEndpoints"], jsii.get(self, "vpcEndpointsInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcStatusInput")
    def vpc_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcStatusInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94fef23d52bb1bc2ad58f1708f9e18311fd5d58ef5405b7c958e3291427c2e49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0faa44d7982288fdc805c4e2b906b0fc3015b033effadef519121d234e7ce9bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0da5297fda08b67f396507c7dad2431b5c44388ff9f2080af97469f2d25bcf34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkId")
    def network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkId"))

    @network_id.setter
    def network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c0f436f0e36132d06aa203e191ca4d82b2f6b0e34778210b6a5e46b764971a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkName")
    def network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkName"))

    @network_name.setter
    def network_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e569aae8455d513c055b6b06b7a876795c249cba1d324b31f834861596e3a7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bfa621fa84400690f9d2f6f6e04620b5307cd0b24b74be1b2ba038add7b3636)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroupIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc24a5904daffd6171d159d23b3563481ca75021c8bccb30eb12fb1df95e88f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa48351c880935883cf3739f24b35477f98a2d838a1867fee641046799fac2a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcStatus")
    def vpc_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcStatus"))

    @vpc_status.setter
    def vpc_status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fd19a3832576b8c775fa597bcdd7344d5bf6e008cab03751d082cc0e5d15180)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcStatus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68203386d9eb4def333de19e6a8681e349e017bd51a15d2344a209dd6b77038)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksConfig",
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
        "network_name": "networkName",
        "creation_time": "creationTime",
        "error_messages": "errorMessages",
        "gcp_network_info": "gcpNetworkInfo",
        "id": "id",
        "network_id": "networkId",
        "security_group_ids": "securityGroupIds",
        "subnet_ids": "subnetIds",
        "vpc_endpoints": "vpcEndpoints",
        "vpc_id": "vpcId",
        "vpc_status": "vpcStatus",
        "workspace_id": "workspaceId",
    },
)
class MwsNetworksConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        network_name: builtins.str,
        creation_time: typing.Optional[jsii.Number] = None,
        error_messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworksErrorMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_network_info: typing.Optional[typing.Union["MwsNetworksGcpNetworkInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoints: typing.Optional[typing.Union["MwsNetworksVpcEndpoints", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        vpc_status: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#account_id MwsNetworks#account_id}.
        :param network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_name MwsNetworks#network_name}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#creation_time MwsNetworks#creation_time}.
        :param error_messages: error_messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_messages MwsNetworks#error_messages}
        :param gcp_network_info: gcp_network_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#gcp_network_info MwsNetworks#gcp_network_info}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#id MwsNetworks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_id MwsNetworks#network_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#security_group_ids MwsNetworks#security_group_ids}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_ids MwsNetworks#subnet_ids}.
        :param vpc_endpoints: vpc_endpoints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_endpoints MwsNetworks#vpc_endpoints}
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.
        :param vpc_status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_status MwsNetworks#vpc_status}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#workspace_id MwsNetworks#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(gcp_network_info, dict):
            gcp_network_info = MwsNetworksGcpNetworkInfo(**gcp_network_info)
        if isinstance(vpc_endpoints, dict):
            vpc_endpoints = MwsNetworksVpcEndpoints(**vpc_endpoints)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b62a972d83ee19ad63bd10b46448f953d1574b436c5548eeb2be57cf36d45fa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument network_name", value=network_name, expected_type=type_hints["network_name"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument error_messages", value=error_messages, expected_type=type_hints["error_messages"])
            check_type(argname="argument gcp_network_info", value=gcp_network_info, expected_type=type_hints["gcp_network_info"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network_id", value=network_id, expected_type=type_hints["network_id"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument vpc_endpoints", value=vpc_endpoints, expected_type=type_hints["vpc_endpoints"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument vpc_status", value=vpc_status, expected_type=type_hints["vpc_status"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "network_name": network_name,
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
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if error_messages is not None:
            self._values["error_messages"] = error_messages
        if gcp_network_info is not None:
            self._values["gcp_network_info"] = gcp_network_info
        if id is not None:
            self._values["id"] = id
        if network_id is not None:
            self._values["network_id"] = network_id
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids
        if vpc_endpoints is not None:
            self._values["vpc_endpoints"] = vpc_endpoints
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id
        if vpc_status is not None:
            self._values["vpc_status"] = vpc_status
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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#account_id MwsNetworks#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_name MwsNetworks#network_name}.'''
        result = self._values.get("network_name")
        assert result is not None, "Required property 'network_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#creation_time MwsNetworks#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def error_messages(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworksErrorMessages"]]]:
        '''error_messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_messages MwsNetworks#error_messages}
        '''
        result = self._values.get("error_messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworksErrorMessages"]]], result)

    @builtins.property
    def gcp_network_info(self) -> typing.Optional["MwsNetworksGcpNetworkInfo"]:
        '''gcp_network_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#gcp_network_info MwsNetworks#gcp_network_info}
        '''
        result = self._values.get("gcp_network_info")
        return typing.cast(typing.Optional["MwsNetworksGcpNetworkInfo"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#id MwsNetworks#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_id MwsNetworks#network_id}.'''
        result = self._values.get("network_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#security_group_ids MwsNetworks#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_ids MwsNetworks#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc_endpoints(self) -> typing.Optional["MwsNetworksVpcEndpoints"]:
        '''vpc_endpoints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_endpoints MwsNetworks#vpc_endpoints}
        '''
        result = self._values.get("vpc_endpoints")
        return typing.cast(typing.Optional["MwsNetworksVpcEndpoints"], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_status MwsNetworks#vpc_status}.'''
        result = self._values.get("vpc_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#workspace_id MwsNetworks#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworksConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksErrorMessages",
    jsii_struct_bases=[],
    name_mapping={"error_message": "errorMessage", "error_type": "errorType"},
)
class MwsNetworksErrorMessages:
    def __init__(
        self,
        *,
        error_message: typing.Optional[builtins.str] = None,
        error_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param error_message: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_message MwsNetworks#error_message}.
        :param error_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_type MwsNetworks#error_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45c0f2449b678964c95fc00372081fe354e4aad9c2b88e2a22ea65b844dce910)
            check_type(argname="argument error_message", value=error_message, expected_type=type_hints["error_message"])
            check_type(argname="argument error_type", value=error_type, expected_type=type_hints["error_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if error_message is not None:
            self._values["error_message"] = error_message
        if error_type is not None:
            self._values["error_type"] = error_type

    @builtins.property
    def error_message(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_message MwsNetworks#error_message}.'''
        result = self._values.get("error_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def error_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#error_type MwsNetworks#error_type}.'''
        result = self._values.get("error_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworksErrorMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworksErrorMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksErrorMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b139686b6505c54c824e9344c359c4e93799371d597f057e1808f9d21710a963)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MwsNetworksErrorMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0504ed8a2fadf79512b2387969034a1758f98ae4dd2cdc8c8f33bcd2b33b786c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MwsNetworksErrorMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c1f43c90e841239e1bff4f8ba8928a3105451a3d99f9e7e4ef3fa5cfb51c75)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b300724b7730c31be7fdaf3b6a356bdc7be05e2d6d3f7055d2dd508865b454d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10a9f527399f939b1767f3a1d5a4ff7e082c0ae68349d55416cfc36a2a111e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworksErrorMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworksErrorMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworksErrorMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63e20d674687bbc2d1fe90d6b331b6a6bc83cb6873b7dd2c833770ea73dbbe45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworksErrorMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksErrorMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be0f6de214b558590b8ea730e00ed3ddd7dd1df7d7850443a8b29dca4745e361)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetErrorMessage")
    def reset_error_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorMessage", []))

    @jsii.member(jsii_name="resetErrorType")
    def reset_error_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorType", []))

    @builtins.property
    @jsii.member(jsii_name="errorMessageInput")
    def error_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="errorTypeInput")
    def error_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="errorMessage")
    def error_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorMessage"))

    @error_message.setter
    def error_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c01430fccccfb326390468ec5e8b2d37a4f1f13b930ed809d07206106873dbdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="errorType")
    def error_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorType"))

    @error_type.setter
    def error_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1389bbe1c303fa2f940b24d6386aaf62c72d657e3f889ef67f5fd1751c50723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworksErrorMessages]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworksErrorMessages]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworksErrorMessages]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38a56173ee4827430890d1d1c0915028970821a0e91f69f2d07d00ea4144d779)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksGcpNetworkInfo",
    jsii_struct_bases=[],
    name_mapping={
        "network_project_id": "networkProjectId",
        "subnet_id": "subnetId",
        "subnet_region": "subnetRegion",
        "vpc_id": "vpcId",
        "pod_ip_range_name": "podIpRangeName",
        "service_ip_range_name": "serviceIpRangeName",
    },
)
class MwsNetworksGcpNetworkInfo:
    def __init__(
        self,
        *,
        network_project_id: builtins.str,
        subnet_id: builtins.str,
        subnet_region: builtins.str,
        vpc_id: builtins.str,
        pod_ip_range_name: typing.Optional[builtins.str] = None,
        service_ip_range_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param network_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_project_id MwsNetworks#network_project_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_id MwsNetworks#subnet_id}.
        :param subnet_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_region MwsNetworks#subnet_region}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.
        :param pod_ip_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#pod_ip_range_name MwsNetworks#pod_ip_range_name}.
        :param service_ip_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#service_ip_range_name MwsNetworks#service_ip_range_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a437c155eaea0552b80bc7c68126d077386fe2564b26ea920b6f6384c2a9ec85)
            check_type(argname="argument network_project_id", value=network_project_id, expected_type=type_hints["network_project_id"])
            check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
            check_type(argname="argument subnet_region", value=subnet_region, expected_type=type_hints["subnet_region"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument pod_ip_range_name", value=pod_ip_range_name, expected_type=type_hints["pod_ip_range_name"])
            check_type(argname="argument service_ip_range_name", value=service_ip_range_name, expected_type=type_hints["service_ip_range_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_project_id": network_project_id,
            "subnet_id": subnet_id,
            "subnet_region": subnet_region,
            "vpc_id": vpc_id,
        }
        if pod_ip_range_name is not None:
            self._values["pod_ip_range_name"] = pod_ip_range_name
        if service_ip_range_name is not None:
            self._values["service_ip_range_name"] = service_ip_range_name

    @builtins.property
    def network_project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#network_project_id MwsNetworks#network_project_id}.'''
        result = self._values.get("network_project_id")
        assert result is not None, "Required property 'network_project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_id MwsNetworks#subnet_id}.'''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#subnet_region MwsNetworks#subnet_region}.'''
        result = self._values.get("subnet_region")
        assert result is not None, "Required property 'subnet_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#vpc_id MwsNetworks#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pod_ip_range_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#pod_ip_range_name MwsNetworks#pod_ip_range_name}.'''
        result = self._values.get("pod_ip_range_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_ip_range_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#service_ip_range_name MwsNetworks#service_ip_range_name}.'''
        result = self._values.get("service_ip_range_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworksGcpNetworkInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworksGcpNetworkInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksGcpNetworkInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ed198309eb2acc5dd7381ee9fbda59cc6dcb916c6291b39faa9e78ec8107252)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPodIpRangeName")
    def reset_pod_ip_range_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPodIpRangeName", []))

    @jsii.member(jsii_name="resetServiceIpRangeName")
    def reset_service_ip_range_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceIpRangeName", []))

    @builtins.property
    @jsii.member(jsii_name="networkProjectIdInput")
    def network_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="podIpRangeNameInput")
    def pod_ip_range_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "podIpRangeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceIpRangeNameInput")
    def service_ip_range_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceIpRangeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetRegionInput")
    def subnet_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property
    @jsii.member(jsii_name="networkProjectId")
    def network_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkProjectId"))

    @network_project_id.setter
    def network_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__451d50f665bf02d171fee33b5bf7caeff330bd524dac54e6627c84a80f9975e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkProjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="podIpRangeName")
    def pod_ip_range_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "podIpRangeName"))

    @pod_ip_range_name.setter
    def pod_ip_range_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc96abbd287719e75abf3a4f6ba1017bb90e9db746d7e917549e1e164a87e873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "podIpRangeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceIpRangeName")
    def service_ip_range_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceIpRangeName"))

    @service_ip_range_name.setter
    def service_ip_range_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5353955804ece6a8e95c1d1210549b69b64964309ed5c85b82beed5a3342107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceIpRangeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5332df59bb9a75538e5f59ee139f3b16e8eb157acd49b0090b0a27a22527453)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetRegion")
    def subnet_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetRegion"))

    @subnet_region.setter
    def subnet_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b19b23d2403d8e1f33f4216f7f889194a43bb9b7015bc059113cd90b4558a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8bd022fa4a4b7772ec264ecc6237ba2fc2a0e09d7c68eb8fc5ca0732204cdfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsNetworksGcpNetworkInfo]:
        return typing.cast(typing.Optional[MwsNetworksGcpNetworkInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MwsNetworksGcpNetworkInfo]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1398a3a224c204ff9f9cc50534d33747bf5dd1213b1d7552787125f18646e928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksVpcEndpoints",
    jsii_struct_bases=[],
    name_mapping={"dataplane_relay": "dataplaneRelay", "rest_api": "restApi"},
)
class MwsNetworksVpcEndpoints:
    def __init__(
        self,
        *,
        dataplane_relay: typing.Sequence[builtins.str],
        rest_api: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param dataplane_relay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#dataplane_relay MwsNetworks#dataplane_relay}.
        :param rest_api: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#rest_api MwsNetworks#rest_api}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0292acb5df0176a3d30869f940166bb03b05255f4b99f0d90f5e839d9c457b41)
            check_type(argname="argument dataplane_relay", value=dataplane_relay, expected_type=type_hints["dataplane_relay"])
            check_type(argname="argument rest_api", value=rest_api, expected_type=type_hints["rest_api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dataplane_relay": dataplane_relay,
            "rest_api": rest_api,
        }

    @builtins.property
    def dataplane_relay(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#dataplane_relay MwsNetworks#dataplane_relay}.'''
        result = self._values.get("dataplane_relay")
        assert result is not None, "Required property 'dataplane_relay' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def rest_api(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_networks#rest_api MwsNetworks#rest_api}.'''
        result = self._values.get("rest_api")
        assert result is not None, "Required property 'rest_api' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworksVpcEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworksVpcEndpointsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworks.MwsNetworksVpcEndpointsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5b2c4f3b6c75bc19743dc26409d2406f1516aeeb7063bb08bb232c381b16c95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="dataplaneRelayInput")
    def dataplane_relay_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataplaneRelayInput"))

    @builtins.property
    @jsii.member(jsii_name="restApiInput")
    def rest_api_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "restApiInput"))

    @builtins.property
    @jsii.member(jsii_name="dataplaneRelay")
    def dataplane_relay(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataplaneRelay"))

    @dataplane_relay.setter
    def dataplane_relay(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51e5555db178bea0588311476339952894e00a2acc244d9b3c480516a6cbc769)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataplaneRelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "restApi"))

    @rest_api.setter
    def rest_api(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c68b73677d04f506304aa8acae5e6ec8fc1836f0345f8f041c381b7e2131d8ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restApi", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MwsNetworksVpcEndpoints]:
        return typing.cast(typing.Optional[MwsNetworksVpcEndpoints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MwsNetworksVpcEndpoints]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__070d69f588228b879f25faef5fc93050f6977ff3b96cf6abd18e24141c1d8f67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MwsNetworks",
    "MwsNetworksConfig",
    "MwsNetworksErrorMessages",
    "MwsNetworksErrorMessagesList",
    "MwsNetworksErrorMessagesOutputReference",
    "MwsNetworksGcpNetworkInfo",
    "MwsNetworksGcpNetworkInfoOutputReference",
    "MwsNetworksVpcEndpoints",
    "MwsNetworksVpcEndpointsOutputReference",
]

publication.publish()

def _typecheckingstub__6b6a07da38e683c274d1086738200902b979f438cc6e2ae7545a68654459943d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: builtins.str,
    network_name: builtins.str,
    creation_time: typing.Optional[jsii.Number] = None,
    error_messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworksErrorMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_network_info: typing.Optional[typing.Union[MwsNetworksGcpNetworkInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_id: typing.Optional[builtins.str] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_endpoints: typing.Optional[typing.Union[MwsNetworksVpcEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_id: typing.Optional[builtins.str] = None,
    vpc_status: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__ef34f4626636f0288f8a45055bef65a3e78d81aabbe2c88e878a403d875a15b5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ffe74c25a3df5bdcc9c113c32d17ed1a98fa6e04ebcaafab53ea41d8f5f92bd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworksErrorMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94fef23d52bb1bc2ad58f1708f9e18311fd5d58ef5405b7c958e3291427c2e49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0faa44d7982288fdc805c4e2b906b0fc3015b033effadef519121d234e7ce9bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0da5297fda08b67f396507c7dad2431b5c44388ff9f2080af97469f2d25bcf34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c0f436f0e36132d06aa203e191ca4d82b2f6b0e34778210b6a5e46b764971a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e569aae8455d513c055b6b06b7a876795c249cba1d324b31f834861596e3a7eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfa621fa84400690f9d2f6f6e04620b5307cd0b24b74be1b2ba038add7b3636(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc24a5904daffd6171d159d23b3563481ca75021c8bccb30eb12fb1df95e88f9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa48351c880935883cf3739f24b35477f98a2d838a1867fee641046799fac2a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fd19a3832576b8c775fa597bcdd7344d5bf6e008cab03751d082cc0e5d15180(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68203386d9eb4def333de19e6a8681e349e017bd51a15d2344a209dd6b77038(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b62a972d83ee19ad63bd10b46448f953d1574b436c5548eeb2be57cf36d45fa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    network_name: builtins.str,
    creation_time: typing.Optional[jsii.Number] = None,
    error_messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworksErrorMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_network_info: typing.Optional[typing.Union[MwsNetworksGcpNetworkInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_id: typing.Optional[builtins.str] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_endpoints: typing.Optional[typing.Union[MwsNetworksVpcEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_id: typing.Optional[builtins.str] = None,
    vpc_status: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45c0f2449b678964c95fc00372081fe354e4aad9c2b88e2a22ea65b844dce910(
    *,
    error_message: typing.Optional[builtins.str] = None,
    error_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b139686b6505c54c824e9344c359c4e93799371d597f057e1808f9d21710a963(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0504ed8a2fadf79512b2387969034a1758f98ae4dd2cdc8c8f33bcd2b33b786c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c1f43c90e841239e1bff4f8ba8928a3105451a3d99f9e7e4ef3fa5cfb51c75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b300724b7730c31be7fdaf3b6a356bdc7be05e2d6d3f7055d2dd508865b454d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10a9f527399f939b1767f3a1d5a4ff7e082c0ae68349d55416cfc36a2a111e09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e20d674687bbc2d1fe90d6b331b6a6bc83cb6873b7dd2c833770ea73dbbe45(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworksErrorMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be0f6de214b558590b8ea730e00ed3ddd7dd1df7d7850443a8b29dca4745e361(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c01430fccccfb326390468ec5e8b2d37a4f1f13b930ed809d07206106873dbdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1389bbe1c303fa2f940b24d6386aaf62c72d657e3f889ef67f5fd1751c50723(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38a56173ee4827430890d1d1c0915028970821a0e91f69f2d07d00ea4144d779(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworksErrorMessages]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a437c155eaea0552b80bc7c68126d077386fe2564b26ea920b6f6384c2a9ec85(
    *,
    network_project_id: builtins.str,
    subnet_id: builtins.str,
    subnet_region: builtins.str,
    vpc_id: builtins.str,
    pod_ip_range_name: typing.Optional[builtins.str] = None,
    service_ip_range_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed198309eb2acc5dd7381ee9fbda59cc6dcb916c6291b39faa9e78ec8107252(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__451d50f665bf02d171fee33b5bf7caeff330bd524dac54e6627c84a80f9975e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc96abbd287719e75abf3a4f6ba1017bb90e9db746d7e917549e1e164a87e873(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5353955804ece6a8e95c1d1210549b69b64964309ed5c85b82beed5a3342107(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5332df59bb9a75538e5f59ee139f3b16e8eb157acd49b0090b0a27a22527453(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b19b23d2403d8e1f33f4216f7f889194a43bb9b7015bc059113cd90b4558a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8bd022fa4a4b7772ec264ecc6237ba2fc2a0e09d7c68eb8fc5ca0732204cdfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1398a3a224c204ff9f9cc50534d33747bf5dd1213b1d7552787125f18646e928(
    value: typing.Optional[MwsNetworksGcpNetworkInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0292acb5df0176a3d30869f940166bb03b05255f4b99f0d90f5e839d9c457b41(
    *,
    dataplane_relay: typing.Sequence[builtins.str],
    rest_api: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b2c4f3b6c75bc19743dc26409d2406f1516aeeb7063bb08bb232c381b16c95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51e5555db178bea0588311476339952894e00a2acc244d9b3c480516a6cbc769(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c68b73677d04f506304aa8acae5e6ec8fc1836f0345f8f041c381b7e2131d8ae(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__070d69f588228b879f25faef5fc93050f6977ff3b96cf6abd18e24141c1d8f67(
    value: typing.Optional[MwsNetworksVpcEndpoints],
) -> None:
    """Type checking stubs"""
    pass
