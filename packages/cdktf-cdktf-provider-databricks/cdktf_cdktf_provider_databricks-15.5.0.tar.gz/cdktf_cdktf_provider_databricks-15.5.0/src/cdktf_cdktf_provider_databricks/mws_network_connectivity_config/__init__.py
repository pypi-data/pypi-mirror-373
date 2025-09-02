r'''
# `databricks_mws_network_connectivity_config`

Refer to the Terraform Registry for docs: [`databricks_mws_network_connectivity_config`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config).
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


class MwsNetworkConnectivityConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config databricks_mws_network_connectivity_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        region: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        egress_config: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
        updated_time: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config databricks_mws_network_connectivity_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#name MwsNetworkConnectivityConfig#name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#region MwsNetworkConnectivityConfig#region}.
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#account_id MwsNetworkConnectivityConfig#account_id}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.
        :param egress_config: egress_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#egress_config MwsNetworkConnectivityConfig#egress_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#id MwsNetworkConnectivityConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f68ff1c9e5004d17defa066c78acb8d14237d744ab60a8419058556688707dff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MwsNetworkConnectivityConfigConfig(
            name=name,
            region=region,
            account_id=account_id,
            creation_time=creation_time,
            egress_config=egress_config,
            id=id,
            network_connectivity_config_id=network_connectivity_config_id,
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
        '''Generates CDKTF code for importing a MwsNetworkConnectivityConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MwsNetworkConnectivityConfig to import.
        :param import_from_id: The id of the existing MwsNetworkConnectivityConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MwsNetworkConnectivityConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf1c1db7e20b041b0a314763e3357a261187a9102fc66ef73d5a1936a4001f5c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEgressConfig")
    def put_egress_config(
        self,
        *,
        default_rules: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigDefaultRules", typing.Dict[builtins.str, typing.Any]]] = None,
        target_rules: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRules", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param default_rules: default_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#default_rules MwsNetworkConnectivityConfig#default_rules}
        :param target_rules: target_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_rules MwsNetworkConnectivityConfig#target_rules}
        '''
        value = MwsNetworkConnectivityConfigEgressConfig(
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
    ) -> "MwsNetworkConnectivityConfigEgressConfigOutputReference":
        return typing.cast("MwsNetworkConnectivityConfigEgressConfigOutputReference", jsii.get(self, "egressConfig"))

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
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfig"]:
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfig"], jsii.get(self, "egressConfigInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__816fe95926bd56fc526ed9e804c1caaf06404419f0dd4b1358ae2f82beeae580)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18aa1f75be33d4c0508d490652ffd012851d7cbc4bbca82138236c744421cbad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493b0bc9d4e6246e8f87506b59d776c7e4b9e033bafb7aaf18d29b81195801a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__905cd4eb75184f99b9a91bdd32a0f535f4c4124fe04341ce89bad53e5d30198e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc5357379d035f1c7e2fb117cdfd603eef5eb6f2778e8f09feab47298525db87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c69a1490f5b9c43975be1c1b4e8bfc93fc04b99e886e73da50c7d4252248378)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1ab9a149470bf13f85259cc2d5a1a6b03524241e4c7664619a56e2d146f0b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigConfig",
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
        "region": "region",
        "account_id": "accountId",
        "creation_time": "creationTime",
        "egress_config": "egressConfig",
        "id": "id",
        "network_connectivity_config_id": "networkConnectivityConfigId",
        "updated_time": "updatedTime",
    },
)
class MwsNetworkConnectivityConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        region: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[jsii.Number] = None,
        egress_config: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        network_connectivity_config_id: typing.Optional[builtins.str] = None,
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
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#name MwsNetworkConnectivityConfig#name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#region MwsNetworkConnectivityConfig#region}.
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#account_id MwsNetworkConnectivityConfig#account_id}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.
        :param egress_config: egress_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#egress_config MwsNetworkConnectivityConfig#egress_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#id MwsNetworkConnectivityConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(egress_config, dict):
            egress_config = MwsNetworkConnectivityConfigEgressConfig(**egress_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87d7ef57f6139ced50150985e9a7850637913e3cc46ff2538981b2b3d330310f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument egress_config", value=egress_config, expected_type=type_hints["egress_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network_connectivity_config_id", value=network_connectivity_config_id, expected_type=type_hints["network_connectivity_config_id"])
            check_type(argname="argument updated_time", value=updated_time, expected_type=type_hints["updated_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "region": region,
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#name MwsNetworkConnectivityConfig#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#region MwsNetworkConnectivityConfig#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#account_id MwsNetworkConnectivityConfig#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_config(
        self,
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfig"]:
        '''egress_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#egress_config MwsNetworkConnectivityConfig#egress_config}
        '''
        result = self._values.get("egress_config")
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#id MwsNetworkConnectivityConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfig",
    jsii_struct_bases=[],
    name_mapping={"default_rules": "defaultRules", "target_rules": "targetRules"},
)
class MwsNetworkConnectivityConfigEgressConfig:
    def __init__(
        self,
        *,
        default_rules: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigDefaultRules", typing.Dict[builtins.str, typing.Any]]] = None,
        target_rules: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRules", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param default_rules: default_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#default_rules MwsNetworkConnectivityConfig#default_rules}
        :param target_rules: target_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_rules MwsNetworkConnectivityConfig#target_rules}
        '''
        if isinstance(default_rules, dict):
            default_rules = MwsNetworkConnectivityConfigEgressConfigDefaultRules(**default_rules)
        if isinstance(target_rules, dict):
            target_rules = MwsNetworkConnectivityConfigEgressConfigTargetRules(**target_rules)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198adabd2222fa731ab902c65df6b7c5d7d64c6adb188e3292ccf0157b3578fb)
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
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRules"]:
        '''default_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#default_rules MwsNetworkConnectivityConfig#default_rules}
        '''
        result = self._values.get("default_rules")
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRules"], result)

    @builtins.property
    def target_rules(
        self,
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfigTargetRules"]:
        '''target_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_rules MwsNetworkConnectivityConfig#target_rules}
        '''
        result = self._values.get("target_rules")
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfigTargetRules"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRules",
    jsii_struct_bases=[],
    name_mapping={
        "aws_stable_ip_rule": "awsStableIpRule",
        "azure_service_endpoint_rule": "azureServiceEndpointRule",
    },
)
class MwsNetworkConnectivityConfigEgressConfigDefaultRules:
    def __init__(
        self,
        *,
        aws_stable_ip_rule: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_endpoint_rule: typing.Optional[typing.Union["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_stable_ip_rule: aws_stable_ip_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_stable_ip_rule MwsNetworkConnectivityConfig#aws_stable_ip_rule}
        :param azure_service_endpoint_rule: azure_service_endpoint_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_service_endpoint_rule MwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        if isinstance(aws_stable_ip_rule, dict):
            aws_stable_ip_rule = MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(**aws_stable_ip_rule)
        if isinstance(azure_service_endpoint_rule, dict):
            azure_service_endpoint_rule = MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(**azure_service_endpoint_rule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec065b2e535bea476767f923b634e95f5d9f536c563ad768a0d697bc0b433ea)
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
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule"]:
        '''aws_stable_ip_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_stable_ip_rule MwsNetworkConnectivityConfig#aws_stable_ip_rule}
        '''
        result = self._values.get("aws_stable_ip_rule")
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule"], result)

    @builtins.property
    def azure_service_endpoint_rule(
        self,
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule"]:
        '''azure_service_endpoint_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_service_endpoint_rule MwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        result = self._values.get("azure_service_endpoint_rule")
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigDefaultRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule",
    jsii_struct_bases=[],
    name_mapping={"cidr_blocks": "cidrBlocks"},
)
class MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule:
    def __init__(
        self,
        *,
        cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cidr_blocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#cidr_blocks MwsNetworkConnectivityConfig#cidr_blocks}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf27c8d423cc14e03b186ea41d0aac906a6cc027a22af5734d416a5a2d4bd4c)
            check_type(argname="argument cidr_blocks", value=cidr_blocks, expected_type=type_hints["cidr_blocks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cidr_blocks is not None:
            self._values["cidr_blocks"] = cidr_blocks

    @builtins.property
    def cidr_blocks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#cidr_blocks MwsNetworkConnectivityConfig#cidr_blocks}.'''
        result = self._values.get("cidr_blocks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f80fd210878c826edda59751fdce52f26275553c6948fe2be4715972e092013)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae8bfd637d8b1a4226d23915ed962a7c73147b697754e5e4379f7efcae55bc6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrBlocks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c242a49b90e2ea7061619768c354d0aa4f92cb8a17df1ae02c0f70ae54ffd0aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule",
    jsii_struct_bases=[],
    name_mapping={
        "subnets": "subnets",
        "target_region": "targetRegion",
        "target_services": "targetServices",
    },
)
class MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule:
    def __init__(
        self,
        *,
        subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_region: typing.Optional[builtins.str] = None,
        target_services: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#subnets MwsNetworkConnectivityConfig#subnets}.
        :param target_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_region MwsNetworkConnectivityConfig#target_region}.
        :param target_services: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_services MwsNetworkConnectivityConfig#target_services}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36365eb733360e5e62ece1eebbd667656c8c3721ad987aaa38d39ac44a50befa)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#subnets MwsNetworkConnectivityConfig#subnets}.'''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_region MwsNetworkConnectivityConfig#target_region}.'''
        result = self._values.get("target_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_services MwsNetworkConnectivityConfig#target_services}.'''
        result = self._values.get("target_services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93d8a11ab13585fa97ae39fd509e09bb663f094b083526abf7ba3bd1be34045f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__533ca91d71e6ea9cfdd05594533405a19b5d1f93ab1b6fe268d92d112adb1ccb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetRegion")
    def target_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetRegion"))

    @target_region.setter
    def target_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__965c26e5051a4abc173448628de08741edd0f44cd16fe425265f1cf6c7949b25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetServices")
    def target_services(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetServices"))

    @target_services.setter
    def target_services(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5043743abaee47f21d743349ad5469dce30bf20264ec6ee48aa5b881982835f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetServices", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8570459ad420b9f713aee4339e4318e8018505ea74d35562ca36ea2f502223c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df718b0ee8bfe03e33e40e223d305a0d469f4ebf4f849aad33297c9cca873bbf)
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
        :param cidr_blocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#cidr_blocks MwsNetworkConnectivityConfig#cidr_blocks}.
        '''
        value = MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule(
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
        :param subnets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#subnets MwsNetworkConnectivityConfig#subnets}.
        :param target_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_region MwsNetworkConnectivityConfig#target_region}.
        :param target_services: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#target_services MwsNetworkConnectivityConfig#target_services}.
        '''
        value = MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule(
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
    ) -> MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference:
        return typing.cast(MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference, jsii.get(self, "awsStableIpRule"))

    @builtins.property
    @jsii.member(jsii_name="azureServiceEndpointRule")
    def azure_service_endpoint_rule(
        self,
    ) -> MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference:
        return typing.cast(MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference, jsii.get(self, "azureServiceEndpointRule"))

    @builtins.property
    @jsii.member(jsii_name="awsStableIpRuleInput")
    def aws_stable_ip_rule_input(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule], jsii.get(self, "awsStableIpRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="azureServiceEndpointRuleInput")
    def azure_service_endpoint_rule_input(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule], jsii.get(self, "azureServiceEndpointRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__095cd4ed61ceba2c56c5bdff3419891a9f470a3eaedd4dd969a5c49dc5bc6d77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworkConnectivityConfigEgressConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23705d0f6924b598fd179570a12c6493019e9b9e398238b9721fbb4b5246271c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDefaultRules")
    def put_default_rules(
        self,
        *,
        aws_stable_ip_rule: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_endpoint_rule: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_stable_ip_rule: aws_stable_ip_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_stable_ip_rule MwsNetworkConnectivityConfig#aws_stable_ip_rule}
        :param azure_service_endpoint_rule: azure_service_endpoint_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_service_endpoint_rule MwsNetworkConnectivityConfig#azure_service_endpoint_rule}
        '''
        value = MwsNetworkConnectivityConfigEgressConfigDefaultRules(
            aws_stable_ip_rule=aws_stable_ip_rule,
            azure_service_endpoint_rule=azure_service_endpoint_rule,
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultRules", [value]))

    @jsii.member(jsii_name="putTargetRules")
    def put_target_rules(
        self,
        *,
        aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param aws_private_endpoint_rules: aws_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_private_endpoint_rules MwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        :param azure_private_endpoint_rules: azure_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_private_endpoint_rules MwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        value = MwsNetworkConnectivityConfigEgressConfigTargetRules(
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
    ) -> MwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference:
        return typing.cast(MwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference, jsii.get(self, "defaultRules"))

    @builtins.property
    @jsii.member(jsii_name="targetRules")
    def target_rules(
        self,
    ) -> "MwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference":
        return typing.cast("MwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference", jsii.get(self, "targetRules"))

    @builtins.property
    @jsii.member(jsii_name="defaultRulesInput")
    def default_rules_input(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules], jsii.get(self, "defaultRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRulesInput")
    def target_rules_input(
        self,
    ) -> typing.Optional["MwsNetworkConnectivityConfigEgressConfigTargetRules"]:
        return typing.cast(typing.Optional["MwsNetworkConnectivityConfigEgressConfigTargetRules"], jsii.get(self, "targetRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfig]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsNetworkConnectivityConfigEgressConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a030049383f61b0fb94ce61a25e869e27a515281f3e19b46b76ebd8c396b457)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRules",
    jsii_struct_bases=[],
    name_mapping={
        "aws_private_endpoint_rules": "awsPrivateEndpointRules",
        "azure_private_endpoint_rules": "azurePrivateEndpointRules",
    },
)
class MwsNetworkConnectivityConfigEgressConfigTargetRules:
    def __init__(
        self,
        *,
        aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param aws_private_endpoint_rules: aws_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_private_endpoint_rules MwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        :param azure_private_endpoint_rules: azure_private_endpoint_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_private_endpoint_rules MwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50c380fff2c81f111797225aebbc52bba442a9f3c71a76f0ebab33ac011c0f55)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules"]]]:
        '''aws_private_endpoint_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#aws_private_endpoint_rules MwsNetworkConnectivityConfig#aws_private_endpoint_rules}
        '''
        result = self._values.get("aws_private_endpoint_rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules"]]], result)

    @builtins.property
    def azure_private_endpoint_rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules"]]]:
        '''azure_private_endpoint_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#azure_private_endpoint_rules MwsNetworkConnectivityConfig#azure_private_endpoint_rules}
        '''
        result = self._values.get("azure_private_endpoint_rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigTargetRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules",
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
class MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules:
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
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#account_id MwsNetworkConnectivityConfig#account_id}.
        :param connection_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#connection_state MwsNetworkConnectivityConfig#connection_state}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.
        :param deactivated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated MwsNetworkConnectivityConfig#deactivated}.
        :param deactivated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated_at MwsNetworkConnectivityConfig#deactivated_at}.
        :param domain_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#domain_names MwsNetworkConnectivityConfig#domain_names}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#enabled MwsNetworkConnectivityConfig#enabled}.
        :param endpoint_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#endpoint_service MwsNetworkConnectivityConfig#endpoint_service}.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param resource_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#resource_names MwsNetworkConnectivityConfig#resource_names}.
        :param rule_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#rule_id MwsNetworkConnectivityConfig#rule_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.
        :param vpc_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#vpc_endpoint_id MwsNetworkConnectivityConfig#vpc_endpoint_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d8faee76674c50be1e67541e22b68d3e665ab70a307ae93d1f2ac0f251b332)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#account_id MwsNetworkConnectivityConfig#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#connection_state MwsNetworkConnectivityConfig#connection_state}.'''
        result = self._values.get("connection_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deactivated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated MwsNetworkConnectivityConfig#deactivated}.'''
        result = self._values.get("deactivated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deactivated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated_at MwsNetworkConnectivityConfig#deactivated_at}.'''
        result = self._values.get("deactivated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#domain_names MwsNetworkConnectivityConfig#domain_names}.'''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#enabled MwsNetworkConnectivityConfig#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def endpoint_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#endpoint_service MwsNetworkConnectivityConfig#endpoint_service}.'''
        result = self._values.get("endpoint_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#resource_names MwsNetworkConnectivityConfig#resource_names}.'''
        result = self._values.get("resource_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rule_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#rule_id MwsNetworkConnectivityConfig#rule_id}.'''
        result = self._values.get("rule_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#vpc_endpoint_id MwsNetworkConnectivityConfig#vpc_endpoint_id}.'''
        result = self._values.get("vpc_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__681dce11f453201dd3e83ef576bf418cc38b831e375f667a801248040b154652)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9c67dd69b6a64a597a11a5aae07f313413289818c6f49cb608edb2e5c17d8cc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d383e42010ae3f32cbe743c394657f999d6faf5ac5e2a9e93577dca05bbfe47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b165940cf746365d01d5c85881929fc11e67d380975ea63f14a4c595289b04ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8b78799b34e6010d93a7c09d7eab18052942716eafdb55ba6c4232cf717cef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be7ecbe49bef0682b8e59dccbc0e1965bfe978639ad8f5af13e69b5b2f071992)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2aa5938d52a343dcdd04c434407282db4fc42aa5036990a3a7dbd6dd71b375db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3fe15c3013dd5c0af509ad44823d9b23688a66820d05db4df045bc50a9dea0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionState")
    def connection_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionState"))

    @connection_state.setter
    def connection_state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9724777b00df8342af29079fc811edf541f2a429f77722f16cd40a1b986270d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b58a5cc8e6ca9a0f4981febb681f05f6642dd512c30b50d799c8e821ccccb839)
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
            type_hints = typing.get_type_hints(_typecheckingstub__287a7cd84df178a21b27b531cd224b652b9d04ed536d187d5753343dbdd3b5ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivatedAt")
    def deactivated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deactivatedAt"))

    @deactivated_at.setter
    def deactivated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb02c1dda99424f53a28c08289f5fd2770e30b044dbe3d26ff331ee0558d6be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainNames")
    def domain_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainNames"))

    @domain_names.setter
    def domain_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42d3aff0c4a6bef132f4151a40cc21450e52b60bc2b321394100352bebe9c35b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee1a1c1df525357803618f6a4c6b3ff094ed60b8ae1b7ab14fc1007fa4b99c9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpointService")
    def endpoint_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointService"))

    @endpoint_service.setter
    def endpoint_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81c11372968edf83d52086d7fe6d2fc59ac2e0bd53d7dae18c11658b593ea582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73fd5334b4c0a08ab76848c863558c2929af3784d4c6804176ee64cfce416e97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceNames")
    def resource_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceNames"))

    @resource_names.setter
    def resource_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d9aa9cdbfa5263e748bcda1df51b02efadd039c2c0f701e26b5ad409e15d621)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6b0d477c634ceb6362d93cd55fb52697b3cf8b94288555e8671e58e8d0efee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__180d0b5b327f91bb4c842293086b31ea2a0e2bd166a0d97560c0ff2ce219750d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointId"))

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c299ab8b8762c511c96da56df9eef6c6a88b810e747a906abdc40578cfa22fc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c687d9ca6a3a49516f3f130e74536820ac7e8b25b18a9224dda2a1a04f47ee1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules",
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
class MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules:
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
        :param connection_state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#connection_state MwsNetworkConnectivityConfig#connection_state}.
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.
        :param deactivated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated MwsNetworkConnectivityConfig#deactivated}.
        :param deactivated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated_at MwsNetworkConnectivityConfig#deactivated_at}.
        :param domain_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#domain_names MwsNetworkConnectivityConfig#domain_names}.
        :param endpoint_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#endpoint_name MwsNetworkConnectivityConfig#endpoint_name}.
        :param group_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#group_id MwsNetworkConnectivityConfig#group_id}.
        :param network_connectivity_config_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.
        :param resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#resource_id MwsNetworkConnectivityConfig#resource_id}.
        :param rule_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#rule_id MwsNetworkConnectivityConfig#rule_id}.
        :param updated_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc88ac8a6d0ca4fd90d3923db47166c9d7edb8669eadb8ac20fa252f44023a75)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#connection_state MwsNetworkConnectivityConfig#connection_state}.'''
        result = self._values.get("connection_state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#creation_time MwsNetworkConnectivityConfig#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deactivated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated MwsNetworkConnectivityConfig#deactivated}.'''
        result = self._values.get("deactivated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deactivated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#deactivated_at MwsNetworkConnectivityConfig#deactivated_at}.'''
        result = self._values.get("deactivated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#domain_names MwsNetworkConnectivityConfig#domain_names}.'''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#endpoint_name MwsNetworkConnectivityConfig#endpoint_name}.'''
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#group_id MwsNetworkConnectivityConfig#group_id}.'''
        result = self._values.get("group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_connectivity_config_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#network_connectivity_config_id MwsNetworkConnectivityConfig#network_connectivity_config_id}.'''
        result = self._values.get("network_connectivity_config_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#resource_id MwsNetworkConnectivityConfig#resource_id}.'''
        result = self._values.get("resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#rule_id MwsNetworkConnectivityConfig#rule_id}.'''
        result = self._values.get("rule_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/mws_network_connectivity_config#updated_time MwsNetworkConnectivityConfig#updated_time}.'''
        result = self._values.get("updated_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32d61b471180f816649525581e28b0bd47f7d103cf79ebfe3a3a2d34ef5262cf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a44a9400bdc3a899a341c67ee7cb060cee6c1ded51cee68deaf1e50812f8e507)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e37abc4ad7d0ed094abf6077461495ec78d162b17a75307867f5fb671d04b1e8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf7037906020da72f5cad910a2f9837d7499d4411eb72558d8762192c586afcb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__67b6db0856cc8ae88f94a60fbf73de1c89971f32f4672d40c28ada7ef5b28674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8e08588fca1aeb11e0f4a18257f22c3c007a68e9ed744ffa797b902fb0501b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa06645db7d9b58374457fc86b1953b2acf630e03d962f49a81d194247628f5a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70379971028790db802381e5b746f0fe4fc84ea399512162b7ac0b0e0e561359)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64abaca009a493670661683a690da9d4b1a45f06b8250d4c3dcb49159336dfbb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc3f307ea36e0f7c6442b06112311834989fe0ae91b0f986dc222e265720eac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deactivatedAt")
    def deactivated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deactivatedAt"))

    @deactivated_at.setter
    def deactivated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05f7a4da8eac2fd84d6c7eba6386856bffc568808ab010af1e92cc77047dcd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deactivatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainNames")
    def domain_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainNames"))

    @domain_names.setter
    def domain_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b2bb8dcb7c64635ff8f3158271a33fc481e1f8fa4ae252506b0ac2c1c419b4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @endpoint_name.setter
    def endpoint_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb8925c0d0d9e29fbec7b98521709fbe7f3bbb8178c1fb9113e7bd7a3dd0a777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpointName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2197f026376f212eebd9e5b5bd002e4046ee434ba3267274965ba7d7b05188ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkConnectivityConfigId")
    def network_connectivity_config_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkConnectivityConfigId"))

    @network_connectivity_config_id.setter
    def network_connectivity_config_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffea18cf51d80216418c5aa2524e5c7a5e08b8d750dc51f1e26b459e46d8662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkConnectivityConfigId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @resource_id.setter
    def resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93af0ac939c1fbee2bf537e7d07d55c84a6e15195361c6bb7940c0cc7fad5010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03bfb02616f8dfaa323cc6d60ffa69cf34afc779e921810563b6cbe64a58096f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedTime")
    def updated_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedTime"))

    @updated_time.setter
    def updated_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53e11e9bf750e05ca5dadd7fc3cd43978acd17244114bc87ab1ebf22c0412939)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cccab52f9003598363a6403f95365daba4ceaf5292df5748cce9c020e3ab104)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.mwsNetworkConnectivityConfig.MwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad6aef1ee36433112056723f7c6f7762f769932636ad060a1f60c577e45c40ce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAwsPrivateEndpointRules")
    def put_aws_private_endpoint_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__757eb5a516546b99a7318defc84ec012e891c992a88ddf43498f56f42ec3a9ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAwsPrivateEndpointRules", [value]))

    @jsii.member(jsii_name="putAzurePrivateEndpointRules")
    def put_azure_private_endpoint_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63f784bb8a71af5f2c258f8acddffddfe8945baefbcce0e22c3a8cfedb08ce72)
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
    ) -> MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList:
        return typing.cast(MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList, jsii.get(self, "awsPrivateEndpointRules"))

    @builtins.property
    @jsii.member(jsii_name="azurePrivateEndpointRules")
    def azure_private_endpoint_rules(
        self,
    ) -> MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList:
        return typing.cast(MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList, jsii.get(self, "azurePrivateEndpointRules"))

    @builtins.property
    @jsii.member(jsii_name="awsPrivateEndpointRulesInput")
    def aws_private_endpoint_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]], jsii.get(self, "awsPrivateEndpointRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="azurePrivateEndpointRulesInput")
    def azure_private_endpoint_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]], jsii.get(self, "azurePrivateEndpointRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MwsNetworkConnectivityConfigEgressConfigTargetRules]:
        return typing.cast(typing.Optional[MwsNetworkConnectivityConfigEgressConfigTargetRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigTargetRules],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd0d15ea41107f32ef3c2429c031543d57f2a97143ea1045878fae47699f763)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MwsNetworkConnectivityConfig",
    "MwsNetworkConnectivityConfigConfig",
    "MwsNetworkConnectivityConfigEgressConfig",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRules",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRuleOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRuleOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigDefaultRulesOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigTargetRules",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesList",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRulesOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesList",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRulesOutputReference",
    "MwsNetworkConnectivityConfigEgressConfigTargetRulesOutputReference",
]

publication.publish()

def _typecheckingstub__f68ff1c9e5004d17defa066c78acb8d14237d744ab60a8419058556688707dff(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    region: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    egress_config: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__cf1c1db7e20b041b0a314763e3357a261187a9102fc66ef73d5a1936a4001f5c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__816fe95926bd56fc526ed9e804c1caaf06404419f0dd4b1358ae2f82beeae580(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18aa1f75be33d4c0508d490652ffd012851d7cbc4bbca82138236c744421cbad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493b0bc9d4e6246e8f87506b59d776c7e4b9e033bafb7aaf18d29b81195801a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__905cd4eb75184f99b9a91bdd32a0f535f4c4124fe04341ce89bad53e5d30198e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc5357379d035f1c7e2fb117cdfd603eef5eb6f2778e8f09feab47298525db87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c69a1490f5b9c43975be1c1b4e8bfc93fc04b99e886e73da50c7d4252248378(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1ab9a149470bf13f85259cc2d5a1a6b03524241e4c7664619a56e2d146f0b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87d7ef57f6139ced50150985e9a7850637913e3cc46ff2538981b2b3d330310f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    region: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[jsii.Number] = None,
    egress_config: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    network_connectivity_config_id: typing.Optional[builtins.str] = None,
    updated_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198adabd2222fa731ab902c65df6b7c5d7d64c6adb188e3292ccf0157b3578fb(
    *,
    default_rules: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigDefaultRules, typing.Dict[builtins.str, typing.Any]]] = None,
    target_rules: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRules, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec065b2e535bea476767f923b634e95f5d9f536c563ad768a0d697bc0b433ea(
    *,
    aws_stable_ip_rule: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_endpoint_rule: typing.Optional[typing.Union[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf27c8d423cc14e03b186ea41d0aac906a6cc027a22af5734d416a5a2d4bd4c(
    *,
    cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f80fd210878c826edda59751fdce52f26275553c6948fe2be4715972e092013(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae8bfd637d8b1a4226d23915ed962a7c73147b697754e5e4379f7efcae55bc6b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c242a49b90e2ea7061619768c354d0aa4f92cb8a17df1ae02c0f70ae54ffd0aa(
    value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAwsStableIpRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36365eb733360e5e62ece1eebbd667656c8c3721ad987aaa38d39ac44a50befa(
    *,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_region: typing.Optional[builtins.str] = None,
    target_services: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93d8a11ab13585fa97ae39fd509e09bb663f094b083526abf7ba3bd1be34045f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__533ca91d71e6ea9cfdd05594533405a19b5d1f93ab1b6fe268d92d112adb1ccb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__965c26e5051a4abc173448628de08741edd0f44cd16fe425265f1cf6c7949b25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5043743abaee47f21d743349ad5469dce30bf20264ec6ee48aa5b881982835f0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8570459ad420b9f713aee4339e4318e8018505ea74d35562ca36ea2f502223c(
    value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRulesAzureServiceEndpointRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df718b0ee8bfe03e33e40e223d305a0d469f4ebf4f849aad33297c9cca873bbf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__095cd4ed61ceba2c56c5bdff3419891a9f470a3eaedd4dd969a5c49dc5bc6d77(
    value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigDefaultRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23705d0f6924b598fd179570a12c6493019e9b9e398238b9721fbb4b5246271c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a030049383f61b0fb94ce61a25e869e27a515281f3e19b46b76ebd8c396b457(
    value: typing.Optional[MwsNetworkConnectivityConfigEgressConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c380fff2c81f111797225aebbc52bba442a9f3c71a76f0ebab33ac011c0f55(
    *,
    aws_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_private_endpoint_rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d8faee76674c50be1e67541e22b68d3e665ab70a307ae93d1f2ac0f251b332(
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

def _typecheckingstub__681dce11f453201dd3e83ef576bf418cc38b831e375f667a801248040b154652(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9c67dd69b6a64a597a11a5aae07f313413289818c6f49cb608edb2e5c17d8cc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d383e42010ae3f32cbe743c394657f999d6faf5ac5e2a9e93577dca05bbfe47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b165940cf746365d01d5c85881929fc11e67d380975ea63f14a4c595289b04ac(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b78799b34e6010d93a7c09d7eab18052942716eafdb55ba6c4232cf717cef9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be7ecbe49bef0682b8e59dccbc0e1965bfe978639ad8f5af13e69b5b2f071992(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aa5938d52a343dcdd04c434407282db4fc42aa5036990a3a7dbd6dd71b375db(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3fe15c3013dd5c0af509ad44823d9b23688a66820d05db4df045bc50a9dea0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9724777b00df8342af29079fc811edf541f2a429f77722f16cd40a1b986270d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b58a5cc8e6ca9a0f4981febb681f05f6642dd512c30b50d799c8e821ccccb839(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__287a7cd84df178a21b27b531cd224b652b9d04ed536d187d5753343dbdd3b5ac(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb02c1dda99424f53a28c08289f5fd2770e30b044dbe3d26ff331ee0558d6be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42d3aff0c4a6bef132f4151a40cc21450e52b60bc2b321394100352bebe9c35b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1a1c1df525357803618f6a4c6b3ff094ed60b8ae1b7ab14fc1007fa4b99c9e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81c11372968edf83d52086d7fe6d2fc59ac2e0bd53d7dae18c11658b593ea582(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73fd5334b4c0a08ab76848c863558c2929af3784d4c6804176ee64cfce416e97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d9aa9cdbfa5263e748bcda1df51b02efadd039c2c0f701e26b5ad409e15d621(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6b0d477c634ceb6362d93cd55fb52697b3cf8b94288555e8671e58e8d0efee6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__180d0b5b327f91bb4c842293086b31ea2a0e2bd166a0d97560c0ff2ce219750d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c299ab8b8762c511c96da56df9eef6c6a88b810e747a906abdc40578cfa22fc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c687d9ca6a3a49516f3f130e74536820ac7e8b25b18a9224dda2a1a04f47ee1d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc88ac8a6d0ca4fd90d3923db47166c9d7edb8669eadb8ac20fa252f44023a75(
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

def _typecheckingstub__32d61b471180f816649525581e28b0bd47f7d103cf79ebfe3a3a2d34ef5262cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a44a9400bdc3a899a341c67ee7cb060cee6c1ded51cee68deaf1e50812f8e507(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e37abc4ad7d0ed094abf6077461495ec78d162b17a75307867f5fb671d04b1e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf7037906020da72f5cad910a2f9837d7499d4411eb72558d8762192c586afcb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67b6db0856cc8ae88f94a60fbf73de1c89971f32f4672d40c28ada7ef5b28674(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e08588fca1aeb11e0f4a18257f22c3c007a68e9ed744ffa797b902fb0501b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa06645db7d9b58374457fc86b1953b2acf630e03d962f49a81d194247628f5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70379971028790db802381e5b746f0fe4fc84ea399512162b7ac0b0e0e561359(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64abaca009a493670661683a690da9d4b1a45f06b8250d4c3dcb49159336dfbb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3f307ea36e0f7c6442b06112311834989fe0ae91b0f986dc222e265720eac2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05f7a4da8eac2fd84d6c7eba6386856bffc568808ab010af1e92cc77047dcd8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b2bb8dcb7c64635ff8f3158271a33fc481e1f8fa4ae252506b0ac2c1c419b4f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8925c0d0d9e29fbec7b98521709fbe7f3bbb8178c1fb9113e7bd7a3dd0a777(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2197f026376f212eebd9e5b5bd002e4046ee434ba3267274965ba7d7b05188ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffea18cf51d80216418c5aa2524e5c7a5e08b8d750dc51f1e26b459e46d8662(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93af0ac939c1fbee2bf537e7d07d55c84a6e15195361c6bb7940c0cc7fad5010(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03bfb02616f8dfaa323cc6d60ffa69cf34afc779e921810563b6cbe64a58096f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53e11e9bf750e05ca5dadd7fc3cd43978acd17244114bc87ab1ebf22c0412939(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cccab52f9003598363a6403f95365daba4ceaf5292df5748cce9c020e3ab104(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad6aef1ee36433112056723f7c6f7762f769932636ad060a1f60c577e45c40ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__757eb5a516546b99a7318defc84ec012e891c992a88ddf43498f56f42ec3a9ad(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAwsPrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63f784bb8a71af5f2c258f8acddffddfe8945baefbcce0e22c3a8cfedb08ce72(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MwsNetworkConnectivityConfigEgressConfigTargetRulesAzurePrivateEndpointRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd0d15ea41107f32ef3c2429c031543d57f2a97143ea1045878fae47699f763(
    value: typing.Optional[MwsNetworkConnectivityConfigEgressConfigTargetRules],
) -> None:
    """Type checking stubs"""
    pass
