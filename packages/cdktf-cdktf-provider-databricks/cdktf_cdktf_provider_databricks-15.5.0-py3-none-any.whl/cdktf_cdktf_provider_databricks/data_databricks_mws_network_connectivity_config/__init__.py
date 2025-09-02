r'''
# `data_databricks_mws_network_connectivity_config`

Refer to the Terraform Registry for docs: [`data_databricks_mws_network_connectivity_config`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config).
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


class DataDatabricksMwsNetworkConnectivityConfig(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config databricks_mws_network_connectivity_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        egress_config: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        updated_time: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config databricks_mws_network_connectivity_config} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#name DataDatabricksMwsNetworkConnectivityConfig#name}.
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#account_id DataDatabricksMwsNetworkConnectivityConfig#account_id}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.
        :param egress_config: egress_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#egress_config DataDatabricksMwsNetworkConnectivityConfig#egress_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#id DataDatabricksMwsNetworkConnectivityConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#region DataDatabricksMwsNetworkConnectivityConfig#region}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98027aa4ea44215dff2479806dc5eaa5f1a39c2de410b6f4f12618fdf6caf35a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksMwsNetworkConnectivityConfigConfig(
            name=name,
            account_id=account_id,
            creation_time=creation_time,
            egress_config=egress_config,
            id=id,
            network_connectivity_config_id=network_connectivity_config_id,
            region=region,
            updated_time=updated_time,
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
        '''Generates CDKTF code for importing a DataDatabricksMwsNetworkConnectivityConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksMwsNetworkConnectivityConfig to import.
        :param import_from_id: The id of the existing DataDatabricksMwsNetworkConnectivityConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksMwsNetworkConnectivityConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fbabca54ee144a82f072bbc0fe70a8fb867071f431b417f55b8d293446573d7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEgressConfig")
    def put_egress_config(
        self,
        *,
        default_rules: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules", typing.Dict[builtins.str, typing.Any]]] = None,
        target_rules: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param default_rules: default_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#default_rules DataDatabricksMwsNetworkConnectivityConfig#default_rules}
        :param target_rules: target_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_rules DataDatabricksMwsNetworkConnectivityConfig#target_rules}
        '''
        value = DataDatabricksMwsNetworkConnectivityConfigEgressConfig(
            default_rules=default_rules, target_rules=target_rules
        )

        return typing.cast(None, jsii.invoke(self, "putEgressConfig", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetEgressConfig")
    def reset_egress_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNetworkConnectivityConfigId")
    def reset_network_connectivity_config_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkConnectivityConfigId", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetUpdatedTime")
    def reset_updated_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedTime", []))

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
    @jsii.member(jsii_name="egressConfig")
    def egress_config(
        self,
    ) -> "DataDatabricksMwsNetworkConnectivityConfigEgressConfigOutputReference":
        return typing.cast("DataDatabricksMwsNetworkConnectivityConfigEgressConfigOutputReference", jsii.get(self, "egressConfig"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="egressConfigInput")
    def egress_config_input(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfig"]:
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfig"], jsii.get(self, "egressConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigIdInput")
    def network_connectivity_config_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkConnectivityConfigIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedTimeInput")
    def updated_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f29870af004ccec3a753614b3dce38b4fba4bf8edb6983f280333df5d70441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3de377c1d2303e6b1c4aa5bfa591d1f188e284198450cf753d0ec84dcea349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df014ecf8d678dccfcadde46461241019e2db9ee5a934e8c061e6d6197a376a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a4c5124decff17fba56d7b80da5ff40c4185650d29e06c7a0bfc2d10521c10a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b3f0bcb0129f523cd100848cae1e08f2f8e3165c9089240b70dc081b9901b4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5decd51b3e9a79dfbfa1230ebff4557e321e763e77f60c34a1d4c8503e720815)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53c2efb6134a66784152c731a42af295f6fe9923da7ef0772ef7f83a8ee1f1c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigConfig",
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
        "account_id": "accountId",
        "creation_time": "creationTime",
        "egress_config": "egressConfig",
        "id": "id",
        "network_connectivity_config_id": "networkConnectivityConfigId",
        "region": "region",
        "updated_time": "updatedTime",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        account_id: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        egress_config: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        updated_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#name DataDatabricksMwsNetworkConnectivityConfig#name}.
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#account_id DataDatabricksMwsNetworkConnectivityConfig#account_id}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.
        :param egress_config: egress_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#egress_config DataDatabricksMwsNetworkConnectivityConfig#egress_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#id DataDatabricksMwsNetworkConnectivityConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#region DataDatabricksMwsNetworkConnectivityConfig#region}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(egress_config, dict):
            egress_config = DataDatabricksMwsNetworkConnectivityConfigEgressConfig(**egress_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67f9299622569f1f020097b2f8f510b2d79ab5c4a348b82bf973b82451e241b1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument egress_config", value=egress_config, expected_type=type_hints["egress_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network_connectivity_config_id", value=network_connectivity_config_id, expected_type=type_hints["network_connectivity_config_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument updated_time", value=updated_time, expected_type=type_hints["updated_time"])
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if egress_config is not None:
            self._values["egress_config"] = egress_config
        if id is not None:
            self._values["id"] = id
        if network_connectivity_config_id is not None:
            self._values["network_connectivity_config_id"] = network_connectivity_config_id
        if region is not None:
            self._values["region"] = region
        if updated_time is not None:
            self._values["updated_time"] = updated_time

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#name DataDatabricksMwsNetworkConnectivityConfig#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#account_id DataDatabricksMwsNetworkConnectivityConfig#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_config(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfig"]:
        '''egress_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#egress_config DataDatabricksMwsNetworkConnectivityConfig#egress_config}
        '''
        result = self._values.get("egress_config")
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#id DataDatabricksMwsNetworkConnectivityConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#region DataDatabricksMwsNetworkConnectivityConfig#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfig",
    jsii_struct_bases=[],
    name_mapping={"default_rules": "defaultRules", "target_rules": "targetRules"},
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfig:
    def __init__(
        self,
        *,
        default_rules: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules", typing.Dict[builtins.str, typing.Any]]] = None,
        target_rules: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param default_rules: default_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#default_rules DataDatabricksMwsNetworkConnectivityConfig#default_rules}
        :param target_rules: target_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_rules DataDatabricksMwsNetworkConnectivityConfig#target_rules}
        '''
        if isinstance(default_rules, dict):
            default_rules = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules(**default_rules)
        if isinstance(target_rules, dict):
            target_rules = DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules(**target_rules)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d989a58d40f1b291c14c68aa6ca2ad0abb559f75406de0edc9fd3ed26467dc)
            check_type(argname="argument default_rules", value=default_rules, expected_type=type_hints["default_rules"])
            check_type(argname="argument target_rules", value=target_rules, expected_type=type_hints["target_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default_rules is not None:
            self._values["default_rules"] = default_rules
        if target_rules is not None:
            self._values["target_rules"] = target_rules

    @builtins.property
    def default_rules(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules"]:
        '''default_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#default_rules DataDatabricksMwsNetworkConnectivityConfig#default_rules}
        '''
        result = self._values.get("default_rules")
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules"], result)

    @builtins.property
    def target_rules(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules"]:
        '''target_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_rules DataDatabricksMwsNetworkConnectivityConfig#target_rules}
        '''
        result = self._values.get("target_rules")
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules",
    jsii_struct_bases=[],
    name_mapping={
        "aws_stable_ip_rule": "awsStableIpRule",
        "azure_service_endpoint_rule": "azureServiceEndpointRule",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules:
    def __init__(
        self,
        *,
        aws_stable_ip_rule: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_endpoint_rule: typing.Optional[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_stable_ip_rule: aws_stable_ip_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_stable_ip_rule DataDatabricksMwsNetworkConnectivityConfig#aws_stable_ip_rule}
        :param azure_service_endpoint_rule: azure_service_endpoint_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_service_endpoint_rule DataDatabricksMwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        if isinstance(aws_stable_ip_rule, dict):
            aws_stable_ip_rule = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(**aws_stable_ip_rule)
        if isinstance(azure_service_endpoint_rule, dict):
            azure_service_endpoint_rule = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(**azure_service_endpoint_rule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72c53ada5c83dc0aa5752207bf4760d550f74a53f8c711b8994f73787cc0f999)
            check_type(argname="argument aws_stable_ip_rule", value=aws_stable_ip_rule, expected_type=type_hints["aws_stable_ip_rule"])
            check_type(argname="argument azure_service_endpoint_rule", value=azure_service_endpoint_rule, expected_type=type_hints["azure_service_endpoint_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aws_stable_ip_rule is not None:
            self._values["aws_stable_ip_rule"] = aws_stable_ip_rule
        if azure_service_endpoint_rule is not None:
            self._values["azure_service_endpoint_rule"] = azure_service_endpoint_rule

    @builtins.property
    def aws_stable_ip_rule(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule"]:
        '''aws_stable_ip_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_stable_ip_rule DataDatabricksMwsNetworkConnectivityConfig#aws_stable_ip_rule}
        '''
        result = self._values.get("aws_stable_ip_rule")
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule"], result)

    @builtins.property
    def azure_service_endpoint_rule(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule"]:
        '''azure_service_endpoint_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_service_endpoint_rule DataDatabricksMwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        result = self._values.get("azure_service_endpoint_rule")
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule",
    jsii_struct_bases=[],
    name_mapping={"cidr_blocks": "cidrBlocks"},
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule:
    def __init__(
        self,
        *,
        cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cidr_blocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#cidr_blocks DataDatabricksMwsNetworkConnectivityConfig#cidr_blocks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b137c758b544e785620f33250d98fe37d5d1a4d8d8b72127b5f739edaca80f6)
            check_type(argname="argument cidr_blocks", value=cidr_blocks, expected_type=type_hints["cidr_blocks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cidr_blocks is not None:
            self._values["cidr_blocks"] = cidr_blocks

    @builtins.property
    def cidr_blocks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#cidr_blocks DataDatabricksMwsNetworkConnectivityConfig#cidr_blocks}.'''
        result = self._values.get("cidr_blocks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__687b7e74e75862ac28e9f39d27ab4e8709cd8900645b1d3126b06c182405cc4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCidrBlocks")
    def reset_cidr_blocks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCidrBlocks", []))

    @builtins.property
    @jsii.member(jsii_name="cidrBlocksInput")
    def cidr_blocks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cidrBlocksInput"))

    @builtins.property
    @jsii.member(jsii_name="cidrBlocks")
    def cidr_blocks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cidrBlocks"))

    @cidr_blocks.setter
    def cidr_blocks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca8d3a1e24af041550bfdbe472aa37d9c568fc10f301b386f3b42190686ca52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrBlocks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__420ddc61cf4f6b40e2ef0cf4a8e9e3f836a4f208bc756a27f4e2d1ca48d9307b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule",
    jsii_struct_bases=[],
    name_mapping={
        "subnets": "subnets",
        "target_region": "targetRegion",
        "target_services": "targetServices",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule:
    def __init__(
        self,
        *,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_region: typing.Optional[builtins.str] = None,
        target_services: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#subnets DataDatabricksMwsNetworkConnectivityConfig#subnets}.
        :param target_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_region DataDatabricksMwsNetworkConnectivityConfig#target_region}.
        :param target_services: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_services DataDatabricksMwsNetworkConnectivityConfig#target_services}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cd01e96cde3210c13c712777ad4263a4a90ca3e70abefb68bb85c3bce3cbaef)
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument target_region", value=target_region, expected_type=type_hints["target_region"])
            check_type(argname="argument target_services", value=target_services, expected_type=type_hints["target_services"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if subnets is not None:
            self._values["subnets"] = subnets
        if target_region is not None:
            self._values["target_region"] = target_region
        if target_services is not None:
            self._values["target_services"] = target_services

    @builtins.property
    def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#subnets DataDatabricksMwsNetworkConnectivityConfig#subnets}.'''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_region DataDatabricksMwsNetworkConnectivityConfig#target_region}.'''
        result = self._values.get("target_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_services DataDatabricksMwsNetworkConnectivityConfig#target_services}.'''
        result = self._values.get("target_services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c72023e5eb83f9e66958f00d6a40f5e16acb7c1319af7c0289ead65ac9110f3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSubnets")
    def reset_subnets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnets", []))

    @jsii.member(jsii_name="resetTargetRegion")
    def reset_target_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetRegion", []))

    @jsii.member(jsii_name="resetTargetServices")
    def reset_target_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetServices", []))

    @builtins.property
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRegionInput")
    def target_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="targetServicesInput")
    def target_services_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetServicesInput"))

    @builtins.property
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b19e4851e452e341fb14773c99b655e83617c31b918946f426f9512eb18ac0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetRegion")
    def target_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetRegion"))

    @target_region.setter
    def target_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc971495fabf3ab76291d7b4deeec1e129083de263eece1552d81ccaf2f9919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetServices")
    def target_services(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetServices"))

    @target_services.setter
    def target_services(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b07060d6ffffe0a258292093aa49654472c5a4486039e791f45bc1d7332fabf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetServices", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b0ceed8923ab5d4e07564d4e4e8ae1ae357ce7d1106b41d6d3d476071ac0efb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcaf52afae45471bfa14523eea4f34d44c8651eb1fc44478a99f46068ac55b89)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAwsStableIpRule")
    def put_aws_stable_ip_rule(
        self,
        *,
        cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cidr_blocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#cidr_blocks DataDatabricksMwsNetworkConnectivityConfig#cidr_blocks}.
        '''
        value = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(
            cidr_blocks=cidr_blocks
        )

        return typing.cast(None, jsii.invoke(self, "putAwsStableIpRule", [value]))

    @jsii.member(jsii_name="putAzureServiceEndpointRule")
    def put_azure_service_endpoint_rule(
        self,
        *,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_region: typing.Optional[builtins.str] = None,
        target_services: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#subnets DataDatabricksMwsNetworkConnectivityConfig#subnets}.
        :param target_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_region DataDatabricksMwsNetworkConnectivityConfig#target_region}.
        :param target_services: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#target_services DataDatabricksMwsNetworkConnectivityConfig#target_services}.
        '''
        value = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(
            subnets=subnets,
            target_region=target_region,
            target_services=target_services,
        )

        return typing.cast(None, jsii.invoke(self, "putAzureServiceEndpointRule", [value]))

    @jsii.member(jsii_name="resetAwsStableIpRule")
    def reset_aws_stable_ip_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStableIpRule", []))

    @jsii.member(jsii_name="resetAzureServiceEndpointRule")
    def reset_azure_service_endpoint_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureServiceEndpointRule", []))

    @builtins.property
    @jsii.member(jsii_name="awsStableIpRule")
    def aws_stable_ip_rule(
        self,
    ) -> DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference:
        return typing.cast(DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference, jsii.get(self, "awsStableIpRule"))

    @builtins.property
    @jsii.member(jsii_name="azureServiceEndpointRule")
    def azure_service_endpoint_rule(
        self,
    ) -> DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference:
        return typing.cast(DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference, jsii.get(self, "azureServiceEndpointRule"))

    @builtins.property
    @jsii.member(jsii_name="awsStableIpRuleInput")
    def aws_stable_ip_rule_input(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule], jsii.get(self, "awsStableIpRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="azureServiceEndpointRuleInput")
    def azure_service_endpoint_rule_input(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule], jsii.get(self, "azureServiceEndpointRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34c8377352fbdf753ad0e94bf5e4048f58349e205b80b15561e6ba94c1a75028)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b2ecd3318464508a01dd4b09e7530df88b467f6cbc49650442cd4c289239edd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDefaultRules")
    def put_default_rules(
        self,
        *,
        aws_stable_ip_rule: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_endpoint_rule: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_stable_ip_rule: aws_stable_ip_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_stable_ip_rule DataDatabricksMwsNetworkConnectivityConfig#aws_stable_ip_rule}
        :param azure_service_endpoint_rule: azure_service_endpoint_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_service_endpoint_rule DataDatabricksMwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        value = DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules(
            aws_stable_ip_rule=aws_stable_ip_rule,
            azure_service_endpoint_rule=azure_service_endpoint_rule,
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultRules", [value]))

    @jsii.member(jsii_name="putTargetRules")
    def put_target_rules(
        self,
        *,
        aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param aws_private_endpoint_rules: aws_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        :param azure_private_endpoint_rules: azure_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        value = DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules(
            aws_private_endpoint_rules=aws_private_endpoint_rules,
            azure_private_endpoint_rules=azure_private_endpoint_rules,
        )

        return typing.cast(None, jsii.invoke(self, "putTargetRules", [value]))

    @jsii.member(jsii_name="resetDefaultRules")
    def reset_default_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRules", []))

    @jsii.member(jsii_name="resetTargetRules")
    def reset_target_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetRules", []))

    @builtins.property
    @jsii.member(jsii_name="defaultRules")
    def default_rules(
        self,
    ) -> DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference:
        return typing.cast(DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference, jsii.get(self, "defaultRules"))

    @builtins.property
    @jsii.member(jsii_name="targetRules")
    def target_rules(
        self,
    ) -> "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference":
        return typing.cast("DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference", jsii.get(self, "targetRules"))

    @builtins.property
    @jsii.member(jsii_name="defaultRulesInput")
    def default_rules_input(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules], jsii.get(self, "defaultRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRulesInput")
    def target_rules_input(
        self,
    ) -> typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules"]:
        return typing.cast(typing.Optional["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules"], jsii.get(self, "targetRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfig]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ad942a11326e0bbb1d17bb6d920f21d3b534099ed0b464ba91bf53328817ff8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules",
    jsii_struct_bases=[],
    name_mapping={
        "aws_private_endpoint_rules": "awsPrivateEndpointRules",
        "azure_private_endpoint_rules": "azurePrivateEndpointRules",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules:
    def __init__(
        self,
        *,
        aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param aws_private_endpoint_rules: aws_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        :param azure_private_endpoint_rules: azure_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d350c8b94f35433263d5864127132efb2b1e067ec3a31fbbdcdb89d4b083cd)
            check_type(argname="argument aws_private_endpoint_rules", value=aws_private_endpoint_rules, expected_type=type_hints["aws_private_endpoint_rules"])
            check_type(argname="argument azure_private_endpoint_rules", value=azure_private_endpoint_rules, expected_type=type_hints["azure_private_endpoint_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aws_private_endpoint_rules is not None:
            self._values["aws_private_endpoint_rules"] = aws_private_endpoint_rules
        if azure_private_endpoint_rules is not None:
            self._values["azure_private_endpoint_rules"] = azure_private_endpoint_rules

    @builtins.property
    def aws_private_endpoint_rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules"]]]:
        '''aws_private_endpoint_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#aws_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        '''
        result = self._values.get("aws_private_endpoint_rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules"]]], result)

    @builtins.property
    def azure_private_endpoint_rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules"]]]:
        '''azure_private_endpoint_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#azure_private_endpoint_rules DataDatabricksMwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        result = self._values.get("azure_private_endpoint_rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "connection_state": "connectionState",
        "creation_time": "creationTime",
        "deactivated": "deactivated",
        "deactivated_at": "deactivatedAt",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "endpoint_service": "endpointService",
        "network_connectivity_config_id": "networkConnectivityConfigId",
        "resource_names": "resourceNames",
        "rule_id": "ruleId",
        "updated_time": "updatedTime",
        "vpc_endpoint_id": "vpcEndpointId",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules:
    def __init__(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        connection_state: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        deactivated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deactivated_at: typing.Optional[jsii.Number] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        endpoint_service: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
        resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        rule_id: typing.Optional[builtins.str] = None,
        updated_time: typing.Optional[jsii.Number] = None,
        vpc_endpoint_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#account_id DataDatabricksMwsNetworkConnectivityConfig#account_id}.
        :param connection_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#connection_state DataDatabricksMwsNetworkConnectivityConfig#connection_state}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.
        :param deactivated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated DataDatabricksMwsNetworkConnectivityConfig#deactivated}.
        :param deactivated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated_at DataDatabricksMwsNetworkConnectivityConfig#deactivated_at}.
        :param domain_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#domain_names DataDatabricksMwsNetworkConnectivityConfig#domain_names}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#enabled DataDatabricksMwsNetworkConnectivityConfig#enabled}.
        :param endpoint_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#endpoint_service DataDatabricksMwsNetworkConnectivityConfig#endpoint_service}.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param resource_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#resource_names DataDatabricksMwsNetworkConnectivityConfig#resource_names}.
        :param rule_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#rule_id DataDatabricksMwsNetworkConnectivityConfig#rule_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#vpc_endpoint_id DataDatabricksMwsNetworkConnectivityConfig#vpc_endpoint_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1504750fcaec568caae3b860c4e89d338a1ba7f67587f2723522bbad30090e2)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument connection_state", value=connection_state, expected_type=type_hints["connection_state"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument deactivated", value=deactivated, expected_type=type_hints["deactivated"])
            check_type(argname="argument deactivated_at", value=deactivated_at, expected_type=type_hints["deactivated_at"])
            check_type(argname="argument domain_names", value=domain_names, expected_type=type_hints["domain_names"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument endpoint_service", value=endpoint_service, expected_type=type_hints["endpoint_service"])
            check_type(argname="argument network_connectivity_config_id", value=network_connectivity_config_id, expected_type=type_hints["network_connectivity_config_id"])
            check_type(argname="argument resource_names", value=resource_names, expected_type=type_hints["resource_names"])
            check_type(argname="argument rule_id", value=rule_id, expected_type=type_hints["rule_id"])
            check_type(argname="argument updated_time", value=updated_time, expected_type=type_hints["updated_time"])
            check_type(argname="argument vpc_endpoint_id", value=vpc_endpoint_id, expected_type=type_hints["vpc_endpoint_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account_id is not None:
            self._values["account_id"] = account_id
        if connection_state is not None:
            self._values["connection_state"] = connection_state
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if deactivated is not None:
            self._values["deactivated"] = deactivated
        if deactivated_at is not None:
            self._values["deactivated_at"] = deactivated_at
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if endpoint_service is not None:
            self._values["endpoint_service"] = endpoint_service
        if network_connectivity_config_id is not None:
            self._values["network_connectivity_config_id"] = network_connectivity_config_id
        if resource_names is not None:
            self._values["resource_names"] = resource_names
        if rule_id is not None:
            self._values["rule_id"] = rule_id
        if updated_time is not None:
            self._values["updated_time"] = updated_time
        if vpc_endpoint_id is not None:
            self._values["vpc_endpoint_id"] = vpc_endpoint_id

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#account_id DataDatabricksMwsNetworkConnectivityConfig#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#connection_state DataDatabricksMwsNetworkConnectivityConfig#connection_state}.'''
        result = self._values.get("connection_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deactivated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated DataDatabricksMwsNetworkConnectivityConfig#deactivated}.'''
        result = self._values.get("deactivated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deactivated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated_at DataDatabricksMwsNetworkConnectivityConfig#deactivated_at}.'''
        result = self._values.get("deactivated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#domain_names DataDatabricksMwsNetworkConnectivityConfig#domain_names}.'''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#enabled DataDatabricksMwsNetworkConnectivityConfig#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def endpoint_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#endpoint_service DataDatabricksMwsNetworkConnectivityConfig#endpoint_service}.'''
        result = self._values.get("endpoint_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#resource_names DataDatabricksMwsNetworkConnectivityConfig#resource_names}.'''
        result = self._values.get("resource_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rule_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#rule_id DataDatabricksMwsNetworkConnectivityConfig#rule_id}.'''
        result = self._values.get("rule_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#vpc_endpoint_id DataDatabricksMwsNetworkConnectivityConfig#vpc_endpoint_id}.'''
        result = self._values.get("vpc_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e561a9f0a16649712e967589805214f1142aa8a1ea1cec5a7bc2ab8682f46fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae8d733ca5633e7a4917c5d2d3e1e5f21fcc1b09d5c8c4c1792b98af7b85edd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48b32fff8f4dec26c52ba32af906a02b4c2cee4cfba22ac4ceac550cc26308da)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92cd0a92c06c39485b57f4b6e1a12877774c56bd60d9026643128401394b1302)
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
            type_hints = typing.get_type_hints(_typecheckingstub__239b9c85489fe2c8d400f3dd3bcb34d8cd38a42474eae26b76ffaed44926cba0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157b30c020bc5f4431854b0256aef188e7bbb106b990bf737e60d75c30d17926)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ce7c183791685d208db443e186fa9ca596eba643e1a44d2c5964c799257d26d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetConnectionState")
    def reset_connection_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionState", []))

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetDeactivated")
    def reset_deactivated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeactivated", []))

    @jsii.member(jsii_name="resetDeactivatedAt")
    def reset_deactivated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeactivatedAt", []))

    @jsii.member(jsii_name="resetDomainNames")
    def reset_domain_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainNames", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEndpointService")
    def reset_endpoint_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointService", []))

    @jsii.member(jsii_name="resetNetworkConnectivityConfigId")
    def reset_network_connectivity_config_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkConnectivityConfigId", []))

    @jsii.member(jsii_name="resetResourceNames")
    def reset_resource_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceNames", []))

    @jsii.member(jsii_name="resetRuleId")
    def reset_rule_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleId", []))

    @jsii.member(jsii_name="resetUpdatedTime")
    def reset_updated_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedTime", []))

    @jsii.member(jsii_name="resetVpcEndpointId")
    def reset_vpc_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointId", []))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionStateInput")
    def connection_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionStateInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="deactivatedAtInput")
    def deactivated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deactivatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="deactivatedInput")
    def deactivated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deactivatedInput"))

    @builtins.property
    @jsii.member(jsii_name="domainNamesInput")
    def domain_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointServiceInput")
    def endpoint_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigIdInput")
    def network_connectivity_config_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkConnectivityConfigIdInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceNamesInput")
    def resource_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleIdInput")
    def rule_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedTimeInput")
    def updated_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointIdInput")
    def vpc_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf183d2fd2f16da2645c1dadac58cbe9a2c9071a8b78d11accd6ce9437380ecc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionState")
    def connection_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionState"))

    @connection_state.setter
    def connection_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec083d19b83a1916403e6a3a023dd0a9f667ed9179949499486cb31b39e853a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbeb9b76bf29a7861770d9e5c071b87a2ce5483cbedafd450339bb551adc77ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivated")
    def deactivated(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deactivated"))

    @deactivated.setter
    def deactivated(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7edaa2c7aef12c6eab0a8d49bf181b90bf73df6d24c0d6419a95869063cade3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivatedAt")
    def deactivated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deactivatedAt"))

    @deactivated_at.setter
    def deactivated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b65dbf2d2863bbd664518f88a8ec650beb8c889719017810cf30fa4fa46d6bdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainNames")
    def domain_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainNames"))

    @domain_names.setter
    def domain_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cd85fb3d7c67f85ca982c34b40d9fbfa3423be78ce6ea65de918c4b1b9ce21f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82f4f9b301a5762af570f0e712ab78b18cc11766c1394afb3b332716f6e6dbc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpointService")
    def endpoint_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointService"))

    @endpoint_service.setter
    def endpoint_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a7e7d9b56e4d6d63580c9f50034e114b7230ccd500b5a6583ab4cab8d616692)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__704685074645cfbee215bc190dd77c41fd838b5131d7129043abed5505fa1ab6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceNames")
    def resource_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceNames"))

    @resource_names.setter
    def resource_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7374e131d849e4bd5773b033ed64a07a7a9d46aa4564c6493f1a4e924c807a24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca30285a7d016329109f670fab5447df635a81f48eab9b4fa96d3ad744b428a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__713562fc24d9d440458acf04b8c6a9ff654e43df630d0c1c940cce900eb2cc49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointId"))

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0660ce4e22de193d97e30beb308965ec30c8135f12b6941f7a475004b15bb022)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d337e1e72da2630317ee22412f942d0786603d29092c7b96f585e3b63b585000)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules",
    jsii_struct_bases=[],
    name_mapping={
        "connection_state": "connectionState",
        "creation_time": "creationTime",
        "deactivated": "deactivated",
        "deactivated_at": "deactivatedAt",
        "domain_names": "domainNames",
        "endpoint_name": "endpointName",
        "group_id": "groupId",
        "network_connectivity_config_id": "networkConnectivityConfigId",
        "resource_id": "resourceId",
        "rule_id": "ruleId",
        "updated_time": "updatedTime",
    },
)
class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules:
    def __init__(
        self,
        *,
        connection_state: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        deactivated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deactivated_at: typing.Optional[jsii.Number] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        endpoint_name: typing.Optional[builtins.str] = None,
        group_id: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
        resource_id: typing.Optional[builtins.str] = None,
        rule_id: typing.Optional[builtins.str] = None,
        updated_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#connection_state DataDatabricksMwsNetworkConnectivityConfig#connection_state}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.
        :param deactivated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated DataDatabricksMwsNetworkConnectivityConfig#deactivated}.
        :param deactivated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated_at DataDatabricksMwsNetworkConnectivityConfig#deactivated_at}.
        :param domain_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#domain_names DataDatabricksMwsNetworkConnectivityConfig#domain_names}.
        :param endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#endpoint_name DataDatabricksMwsNetworkConnectivityConfig#endpoint_name}.
        :param group_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#group_id DataDatabricksMwsNetworkConnectivityConfig#group_id}.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#resource_id DataDatabricksMwsNetworkConnectivityConfig#resource_id}.
        :param rule_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#rule_id DataDatabricksMwsNetworkConnectivityConfig#rule_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cbc6e170749817421e28a20394e95663ccb5e8faba60f9f8139e91187db2560)
            check_type(argname="argument connection_state", value=connection_state, expected_type=type_hints["connection_state"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument deactivated", value=deactivated, expected_type=type_hints["deactivated"])
            check_type(argname="argument deactivated_at", value=deactivated_at, expected_type=type_hints["deactivated_at"])
            check_type(argname="argument domain_names", value=domain_names, expected_type=type_hints["domain_names"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument group_id", value=group_id, expected_type=type_hints["group_id"])
            check_type(argname="argument network_connectivity_config_id", value=network_connectivity_config_id, expected_type=type_hints["network_connectivity_config_id"])
            check_type(argname="argument resource_id", value=resource_id, expected_type=type_hints["resource_id"])
            check_type(argname="argument rule_id", value=rule_id, expected_type=type_hints["rule_id"])
            check_type(argname="argument updated_time", value=updated_time, expected_type=type_hints["updated_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_state is not None:
            self._values["connection_state"] = connection_state
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if deactivated is not None:
            self._values["deactivated"] = deactivated
        if deactivated_at is not None:
            self._values["deactivated_at"] = deactivated_at
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if endpoint_name is not None:
            self._values["endpoint_name"] = endpoint_name
        if group_id is not None:
            self._values["group_id"] = group_id
        if network_connectivity_config_id is not None:
            self._values["network_connectivity_config_id"] = network_connectivity_config_id
        if resource_id is not None:
            self._values["resource_id"] = resource_id
        if rule_id is not None:
            self._values["rule_id"] = rule_id
        if updated_time is not None:
            self._values["updated_time"] = updated_time

    @builtins.property
    def connection_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#connection_state DataDatabricksMwsNetworkConnectivityConfig#connection_state}.'''
        result = self._values.get("connection_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#creation_time DataDatabricksMwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deactivated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated DataDatabricksMwsNetworkConnectivityConfig#deactivated}.'''
        result = self._values.get("deactivated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deactivated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#deactivated_at DataDatabricksMwsNetworkConnectivityConfig#deactivated_at}.'''
        result = self._values.get("deactivated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#domain_names DataDatabricksMwsNetworkConnectivityConfig#domain_names}.'''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#endpoint_name DataDatabricksMwsNetworkConnectivityConfig#endpoint_name}.'''
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#group_id DataDatabricksMwsNetworkConnectivityConfig#group_id}.'''
        result = self._values.get("group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#network_connectivity_config_id DataDatabricksMwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#resource_id DataDatabricksMwsNetworkConnectivityConfig#resource_id}.'''
        result = self._values.get("resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#rule_id DataDatabricksMwsNetworkConnectivityConfig#rule_id}.'''
        result = self._values.get("rule_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/mws_network_connectivity_config#updated_time DataDatabricksMwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a49df75e4e52b8ccac97adde95fbfc0118d667a79cf661106ea367270806ccee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1e589fdaa9fb493e35c055cb2cc7d142766a7b5a442a19cb06f0108b57d341d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87905127fb443f77630eec30626b5c63623a313e53581922bc6bc9ba6827a2c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e81f0701221a6eab4eefa3e1105111559f7379768bce1cb0f5bb216ca311a1f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0af259dd53463efa075cf63245809984414e6052611de1c97aad35ab7589acfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__464df08f2242f0fbadff22c986033397bb850828a233c22d39d7bd545ef94a99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aeaee543076e8b7c97e5203a46aab311b83ad05024c2002409a8b1fe43d3422e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetConnectionState")
    def reset_connection_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionState", []))

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetDeactivated")
    def reset_deactivated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeactivated", []))

    @jsii.member(jsii_name="resetDeactivatedAt")
    def reset_deactivated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeactivatedAt", []))

    @jsii.member(jsii_name="resetDomainNames")
    def reset_domain_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainNames", []))

    @jsii.member(jsii_name="resetEndpointName")
    def reset_endpoint_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointName", []))

    @jsii.member(jsii_name="resetGroupId")
    def reset_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupId", []))

    @jsii.member(jsii_name="resetNetworkConnectivityConfigId")
    def reset_network_connectivity_config_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkConnectivityConfigId", []))

    @jsii.member(jsii_name="resetResourceId")
    def reset_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceId", []))

    @jsii.member(jsii_name="resetRuleId")
    def reset_rule_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleId", []))

    @jsii.member(jsii_name="resetUpdatedTime")
    def reset_updated_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedTime", []))

    @builtins.property
    @jsii.member(jsii_name="connectionStateInput")
    def connection_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionStateInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="deactivatedAtInput")
    def deactivated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deactivatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="deactivatedInput")
    def deactivated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deactivatedInput"))

    @builtins.property
    @jsii.member(jsii_name="domainNamesInput")
    def domain_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointNameInput")
    def endpoint_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointNameInput"))

    @builtins.property
    @jsii.member(jsii_name="groupIdInput")
    def group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigIdInput")
    def network_connectivity_config_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkConnectivityConfigIdInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceIdInput")
    def resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleIdInput")
    def rule_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedTimeInput")
    def updated_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionState")
    def connection_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionState"))

    @connection_state.setter
    def connection_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea948107eac2542fbf7ad6bfc2d62287918540a0f567fecf69194e5ca9d9490a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df3aaec5d998c625701a90b3d11ce78519f73dbe7aa250987953b35b45f3afb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivated")
    def deactivated(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deactivated"))

    @deactivated.setter
    def deactivated(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5abcea71c6c7eac3cf9d43843669a4a07ec97f80f56183c899d64509fcbeda2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivatedAt")
    def deactivated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deactivatedAt"))

    @deactivated_at.setter
    def deactivated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54bfa95aab3ce383dbaa76832a21e797dd5dff6a646d9aef93c40e8fd818b206)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainNames")
    def domain_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainNames"))

    @domain_names.setter
    def domain_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__679393800e535cb625b4851311ef78f81051a42347f0cb57297be9f3e86e852d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @endpoint_name.setter
    def endpoint_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d27eb04ddc420ac1dbee502a9e581c26001f1e84ff5a2de05a754020300ea263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1c25373a6121199d0f287a06ea4dd2ec92455fc700e6b5bd5f4d6a4e67f8318)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb622456c131603c75092c5822bfbe3cf419b33b557e0b8fa23f44985002edbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617c431ac0010cfce1becdc2984feb22ba9b9342446f75f5da65f5a0cb6da169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f09fbf0222cd5a1504f9f303b30a6c19ee1080a7c6f4f3707c22ea42512d38e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__248bea88d93db07d8261e960fa3cdc3c98a0c1b7ad99ff38fb32a5b069bd94b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0db708b78cba2012af01bfe1c43643f758a71b6486c5996d56d66f40f1d6bdde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksMwsNetworkConnectivityConfig.DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__514e066d180d7937ba04a87222a4c022c0cc49dec655866717e2d13008356f1a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAwsPrivateEndpointRules")
    def put_aws_private_endpoint_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__003a81aee88a4db9ede09fccf9222ff36d2b242d2d2f18243460b3b37c84e4c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAwsPrivateEndpointRules", [value]))

    @jsii.member(jsii_name="putAzurePrivateEndpointRules")
    def put_azure_private_endpoint_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__285310b6329c10349eb94b55a43d23acc8deb06f5c18fb14a4ac503ce534b1c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzurePrivateEndpointRules", [value]))

    @jsii.member(jsii_name="resetAwsPrivateEndpointRules")
    def reset_aws_private_endpoint_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsPrivateEndpointRules", []))

    @jsii.member(jsii_name="resetAzurePrivateEndpointRules")
    def reset_azure_private_endpoint_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzurePrivateEndpointRules", []))

    @builtins.property
    @jsii.member(jsii_name="awsPrivateEndpointRules")
    def aws_private_endpoint_rules(
        self,
    ) -> DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList:
        return typing.cast(DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList, jsii.get(self, "awsPrivateEndpointRules"))

    @builtins.property
    @jsii.member(jsii_name="azurePrivateEndpointRules")
    def azure_private_endpoint_rules(
        self,
    ) -> DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList:
        return typing.cast(DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList, jsii.get(self, "azurePrivateEndpointRules"))

    @builtins.property
    @jsii.member(jsii_name="awsPrivateEndpointRulesInput")
    def aws_private_endpoint_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]], jsii.get(self, "awsPrivateEndpointRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="azurePrivateEndpointRulesInput")
    def azure_private_endpoint_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]], jsii.get(self, "azurePrivateEndpointRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules]:
        return typing.cast(typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c04e4f5d7ddd88e19aa9c424565cd0d069018f0225e578e87f03ea97468f02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksMwsNetworkConnectivityConfig",
    "DataDatabricksMwsNetworkConnectivityConfigConfig",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfig",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference",
    "DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference",
]

publication.publish()

def _typecheckingstub__98027aa4ea44215dff2479806dc5eaa5f1a39c2de410b6f4f12618fdf6caf35a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    egress_config: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    updated_time: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__3fbabca54ee144a82f072bbc0fe70a8fb867071f431b417f55b8d293446573d7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f29870af004ccec3a753614b3dce38b4fba4bf8edb6983f280333df5d70441(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3de377c1d2303e6b1c4aa5bfa591d1f188e284198450cf753d0ec84dcea349(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df014ecf8d678dccfcadde46461241019e2db9ee5a934e8c061e6d6197a376a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a4c5124decff17fba56d7b80da5ff40c4185650d29e06c7a0bfc2d10521c10a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b3f0bcb0129f523cd100848cae1e08f2f8e3165c9089240b70dc081b9901b4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5decd51b3e9a79dfbfa1230ebff4557e321e763e77f60c34a1d4c8503e720815(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53c2efb6134a66784152c731a42af295f6fe9923da7ef0772ef7f83a8ee1f1c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f9299622569f1f020097b2f8f510b2d79ab5c4a348b82bf973b82451e241b1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    egress_config: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    updated_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d989a58d40f1b291c14c68aa6ca2ad0abb559f75406de0edc9fd3ed26467dc(
    *,
    default_rules: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules, typing.Dict[builtins.str, typing.Any]]] = None,
    target_rules: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72c53ada5c83dc0aa5752207bf4760d550f74a53f8c711b8994f73787cc0f999(
    *,
    aws_stable_ip_rule: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_endpoint_rule: typing.Optional[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b137c758b544e785620f33250d98fe37d5d1a4d8d8b72127b5f739edaca80f6(
    *,
    cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687b7e74e75862ac28e9f39d27ab4e8709cd8900645b1d3126b06c182405cc4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca8d3a1e24af041550bfdbe472aa37d9c568fc10f301b386f3b42190686ca52(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__420ddc61cf4f6b40e2ef0cf4a8e9e3f836a4f208bc756a27f4e2d1ca48d9307b(
    value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cd01e96cde3210c13c712777ad4263a4a90ca3e70abefb68bb85c3bce3cbaef(
    *,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_region: typing.Optional[builtins.str] = None,
    target_services: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c72023e5eb83f9e66958f00d6a40f5e16acb7c1319af7c0289ead65ac9110f3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b19e4851e452e341fb14773c99b655e83617c31b918946f426f9512eb18ac0e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc971495fabf3ab76291d7b4deeec1e129083de263eece1552d81ccaf2f9919(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b07060d6ffffe0a258292093aa49654472c5a4486039e791f45bc1d7332fabf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b0ceed8923ab5d4e07564d4e4e8ae1ae357ce7d1106b41d6d3d476071ac0efb(
    value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcaf52afae45471bfa14523eea4f34d44c8651eb1fc44478a99f46068ac55b89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34c8377352fbdf753ad0e94bf5e4048f58349e205b80b15561e6ba94c1a75028(
    value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigDefaultRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b2ecd3318464508a01dd4b09e7530df88b467f6cbc49650442cd4c289239edd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ad942a11326e0bbb1d17bb6d920f21d3b534099ed0b464ba91bf53328817ff8(
    value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d350c8b94f35433263d5864127132efb2b1e067ec3a31fbbdcdb89d4b083cd(
    *,
    aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1504750fcaec568caae3b860c4e89d338a1ba7f67587f2723522bbad30090e2(
    *,
    account_id: typing.Optional[builtins.str] = None,
    connection_state: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    deactivated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deactivated_at: typing.Optional[jsii.Number] = None,
    domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    endpoint_service: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
    resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    rule_id: typing.Optional[builtins.str] = None,
    updated_time: typing.Optional[jsii.Number] = None,
    vpc_endpoint_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e561a9f0a16649712e967589805214f1142aa8a1ea1cec5a7bc2ab8682f46fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae8d733ca5633e7a4917c5d2d3e1e5f21fcc1b09d5c8c4c1792b98af7b85edd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48b32fff8f4dec26c52ba32af906a02b4c2cee4cfba22ac4ceac550cc26308da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92cd0a92c06c39485b57f4b6e1a12877774c56bd60d9026643128401394b1302(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__239b9c85489fe2c8d400f3dd3bcb34d8cd38a42474eae26b76ffaed44926cba0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157b30c020bc5f4431854b0256aef188e7bbb106b990bf737e60d75c30d17926(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ce7c183791685d208db443e186fa9ca596eba643e1a44d2c5964c799257d26d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf183d2fd2f16da2645c1dadac58cbe9a2c9071a8b78d11accd6ce9437380ecc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec083d19b83a1916403e6a3a023dd0a9f667ed9179949499486cb31b39e853a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbeb9b76bf29a7861770d9e5c071b87a2ce5483cbedafd450339bb551adc77ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7edaa2c7aef12c6eab0a8d49bf181b90bf73df6d24c0d6419a95869063cade3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b65dbf2d2863bbd664518f88a8ec650beb8c889719017810cf30fa4fa46d6bdc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cd85fb3d7c67f85ca982c34b40d9fbfa3423be78ce6ea65de918c4b1b9ce21f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82f4f9b301a5762af570f0e712ab78b18cc11766c1394afb3b332716f6e6dbc7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a7e7d9b56e4d6d63580c9f50034e114b7230ccd500b5a6583ab4cab8d616692(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__704685074645cfbee215bc190dd77c41fd838b5131d7129043abed5505fa1ab6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7374e131d849e4bd5773b033ed64a07a7a9d46aa4564c6493f1a4e924c807a24(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca30285a7d016329109f670fab5447df635a81f48eab9b4fa96d3ad744b428a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__713562fc24d9d440458acf04b8c6a9ff654e43df630d0c1c940cce900eb2cc49(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0660ce4e22de193d97e30beb308965ec30c8135f12b6941f7a475004b15bb022(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d337e1e72da2630317ee22412f942d0786603d29092c7b96f585e3b63b585000(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cbc6e170749817421e28a20394e95663ccb5e8faba60f9f8139e91187db2560(
    *,
    connection_state: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    deactivated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deactivated_at: typing.Optional[jsii.Number] = None,
    domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    endpoint_name: typing.Optional[builtins.str] = None,
    group_id: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
    resource_id: typing.Optional[builtins.str] = None,
    rule_id: typing.Optional[builtins.str] = None,
    updated_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49df75e4e52b8ccac97adde95fbfc0118d667a79cf661106ea367270806ccee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e589fdaa9fb493e35c055cb2cc7d142766a7b5a442a19cb06f0108b57d341d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87905127fb443f77630eec30626b5c63623a313e53581922bc6bc9ba6827a2c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e81f0701221a6eab4eefa3e1105111559f7379768bce1cb0f5bb216ca311a1f5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0af259dd53463efa075cf63245809984414e6052611de1c97aad35ab7589acfc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__464df08f2242f0fbadff22c986033397bb850828a233c22d39d7bd545ef94a99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeaee543076e8b7c97e5203a46aab311b83ad05024c2002409a8b1fe43d3422e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea948107eac2542fbf7ad6bfc2d62287918540a0f567fecf69194e5ca9d9490a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df3aaec5d998c625701a90b3d11ce78519f73dbe7aa250987953b35b45f3afb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5abcea71c6c7eac3cf9d43843669a4a07ec97f80f56183c899d64509fcbeda2c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54bfa95aab3ce383dbaa76832a21e797dd5dff6a646d9aef93c40e8fd818b206(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679393800e535cb625b4851311ef78f81051a42347f0cb57297be9f3e86e852d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d27eb04ddc420ac1dbee502a9e581c26001f1e84ff5a2de05a754020300ea263(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1c25373a6121199d0f287a06ea4dd2ec92455fc700e6b5bd5f4d6a4e67f8318(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb622456c131603c75092c5822bfbe3cf419b33b557e0b8fa23f44985002edbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617c431ac0010cfce1becdc2984feb22ba9b9342446f75f5da65f5a0cb6da169(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f09fbf0222cd5a1504f9f303b30a6c19ee1080a7c6f4f3707c22ea42512d38e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__248bea88d93db07d8261e960fa3cdc3c98a0c1b7ad99ff38fb32a5b069bd94b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0db708b78cba2012af01bfe1c43643f758a71b6486c5996d56d66f40f1d6bdde(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__514e066d180d7937ba04a87222a4c022c0cc49dec655866717e2d13008356f1a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__003a81aee88a4db9ede09fccf9222ff36d2b242d2d2f18243460b3b37c84e4c6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__285310b6329c10349eb94b55a43d23acc8deb06f5c18fb14a4ac503ce534b1c9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c04e4f5d7ddd88e19aa9c424565cd0d069018f0225e578e87f03ea97468f02(
    value: typing.Optional[DataDatabricksMwsNetworkConnectivityConfigEgressConfigTargetRules],
) -> None:
    """Type checking stubs"""
    pass
