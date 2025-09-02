r'''
# `data_databricks_account_network_policy`

Refer to the Terraform Registry for docs: [`data_databricks_account_network_policy`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy).
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


class DataDatabricksAccountNetworkPolicy(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy databricks_account_network_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        egress: typing.Optional[typing.Union["DataDatabricksAccountNetworkPolicyEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        network_policy_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy databricks_account_network_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#account_id DataDatabricksAccountNetworkPolicy#account_id}.
        :param egress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#egress DataDatabricksAccountNetworkPolicy#egress}.
        :param network_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_policy_id DataDatabricksAccountNetworkPolicy#network_policy_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa916696b8a1f3d8c1e060d17d64385e407b1710f3fa9fa761d5b1587d8f2ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAccountNetworkPolicyConfig(
            account_id=account_id,
            egress=egress,
            network_policy_id=network_policy_id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataDatabricksAccountNetworkPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAccountNetworkPolicy to import.
        :param import_from_id: The id of the existing DataDatabricksAccountNetworkPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAccountNetworkPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b38ca795290007d91e09caf31410da69fd6354afb2fe24979a9f74eaf383791c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEgress")
    def put_egress(
        self,
        *,
        network_access: typing.Optional[typing.Union["DataDatabricksAccountNetworkPolicyEgressNetworkAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_access DataDatabricksAccountNetworkPolicy#network_access}.
        '''
        value = DataDatabricksAccountNetworkPolicyEgress(network_access=network_access)

        return typing.cast(None, jsii.invoke(self, "putEgress", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetEgress")
    def reset_egress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgress", []))

    @jsii.member(jsii_name="resetNetworkPolicyId")
    def reset_network_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkPolicyId", []))

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
    @jsii.member(jsii_name="egress")
    def egress(self) -> "DataDatabricksAccountNetworkPolicyEgressOutputReference":
        return typing.cast("DataDatabricksAccountNetworkPolicyEgressOutputReference", jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="egressInput")
    def egress_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPolicyEgress"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPolicyEgress"]], jsii.get(self, "egressInput"))

    @builtins.property
    @jsii.member(jsii_name="networkPolicyIdInput")
    def network_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ac83a03b91c63cac183b696ab81ef56549bc8c673e09b231cadcede354a554)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkPolicyId")
    def network_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkPolicyId"))

    @network_policy_id.setter
    def network_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ce35450ba90009f4864b91a6ddfd11ab40fd6efa3476dc0282a2b302f91df3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkPolicyId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyConfig",
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
        "egress": "egress",
        "network_policy_id": "networkPolicyId",
    },
)
class DataDatabricksAccountNetworkPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: typing.Optional[builtins.str] = None,
        egress: typing.Optional[typing.Union["DataDatabricksAccountNetworkPolicyEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        network_policy_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#account_id DataDatabricksAccountNetworkPolicy#account_id}.
        :param egress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#egress DataDatabricksAccountNetworkPolicy#egress}.
        :param network_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_policy_id DataDatabricksAccountNetworkPolicy#network_policy_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(egress, dict):
            egress = DataDatabricksAccountNetworkPolicyEgress(**egress)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09aa6e9feddfae615244c3359fd4a38fbd830854743b96f6403b1bb139c5b215)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument egress", value=egress, expected_type=type_hints["egress"])
            check_type(argname="argument network_policy_id", value=network_policy_id, expected_type=type_hints["network_policy_id"])
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if egress is not None:
            self._values["egress"] = egress
        if network_policy_id is not None:
            self._values["network_policy_id"] = network_policy_id

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#account_id DataDatabricksAccountNetworkPolicy#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def egress(self) -> typing.Optional["DataDatabricksAccountNetworkPolicyEgress"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#egress DataDatabricksAccountNetworkPolicy#egress}.'''
        result = self._values.get("egress")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPolicyEgress"], result)

    @builtins.property
    def network_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_policy_id DataDatabricksAccountNetworkPolicy#network_policy_id}.'''
        result = self._values.get("network_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgress",
    jsii_struct_bases=[],
    name_mapping={"network_access": "networkAccess"},
)
class DataDatabricksAccountNetworkPolicyEgress:
    def __init__(
        self,
        *,
        network_access: typing.Optional[typing.Union["DataDatabricksAccountNetworkPolicyEgressNetworkAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_access DataDatabricksAccountNetworkPolicy#network_access}.
        '''
        if isinstance(network_access, dict):
            network_access = DataDatabricksAccountNetworkPolicyEgressNetworkAccess(**network_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b7ec543ad23dbe2a8fded08872e30f67f7a736b3af223501ec0304e50778b14)
            check_type(argname="argument network_access", value=network_access, expected_type=type_hints["network_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if network_access is not None:
            self._values["network_access"] = network_access

    @builtins.property
    def network_access(
        self,
    ) -> typing.Optional["DataDatabricksAccountNetworkPolicyEgressNetworkAccess"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#network_access DataDatabricksAccountNetworkPolicy#network_access}.'''
        result = self._values.get("network_access")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPolicyEgressNetworkAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccess",
    jsii_struct_bases=[],
    name_mapping={
        "restriction_mode": "restrictionMode",
        "allowed_internet_destinations": "allowedInternetDestinations",
        "allowed_storage_destinations": "allowedStorageDestinations",
        "policy_enforcement": "policyEnforcement",
    },
)
class DataDatabricksAccountNetworkPolicyEgressNetworkAccess:
    def __init__(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union["DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#restriction_mode DataDatabricksAccountNetworkPolicy#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_internet_destinations DataDatabricksAccountNetworkPolicy#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_storage_destinations DataDatabricksAccountNetworkPolicy#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#policy_enforcement DataDatabricksAccountNetworkPolicy#policy_enforcement}.
        '''
        if isinstance(policy_enforcement, dict):
            policy_enforcement = DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(**policy_enforcement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca761b85c80c5b383d7913db907ffb0676bc6cc9a99ebd6c32bc8be283d9d9cc)
            check_type(argname="argument restriction_mode", value=restriction_mode, expected_type=type_hints["restriction_mode"])
            check_type(argname="argument allowed_internet_destinations", value=allowed_internet_destinations, expected_type=type_hints["allowed_internet_destinations"])
            check_type(argname="argument allowed_storage_destinations", value=allowed_storage_destinations, expected_type=type_hints["allowed_storage_destinations"])
            check_type(argname="argument policy_enforcement", value=policy_enforcement, expected_type=type_hints["policy_enforcement"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "restriction_mode": restriction_mode,
        }
        if allowed_internet_destinations is not None:
            self._values["allowed_internet_destinations"] = allowed_internet_destinations
        if allowed_storage_destinations is not None:
            self._values["allowed_storage_destinations"] = allowed_storage_destinations
        if policy_enforcement is not None:
            self._values["policy_enforcement"] = policy_enforcement

    @builtins.property
    def restriction_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#restriction_mode DataDatabricksAccountNetworkPolicy#restriction_mode}.'''
        result = self._values.get("restriction_mode")
        assert result is not None, "Required property 'restriction_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_internet_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_internet_destinations DataDatabricksAccountNetworkPolicy#allowed_internet_destinations}.'''
        result = self._values.get("allowed_internet_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations"]]], result)

    @builtins.property
    def allowed_storage_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_storage_destinations DataDatabricksAccountNetworkPolicy#allowed_storage_destinations}.'''
        result = self._values.get("allowed_storage_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations"]]], result)

    @builtins.property
    def policy_enforcement(
        self,
    ) -> typing.Optional["DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#policy_enforcement DataDatabricksAccountNetworkPolicy#policy_enforcement}.'''
        result = self._values.get("policy_enforcement")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyEgressNetworkAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "internet_destination_type": "internetDestinationType",
    },
)
class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations:
    def __init__(
        self,
        *,
        destination: typing.Optional[builtins.str] = None,
        internet_destination_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#destination DataDatabricksAccountNetworkPolicy#destination}.
        :param internet_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#internet_destination_type DataDatabricksAccountNetworkPolicy#internet_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5800dc017d2e2f41e9bd6472ff2e7a95d9ac2b5bd93e544f664df69fc5c9124a)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument internet_destination_type", value=internet_destination_type, expected_type=type_hints["internet_destination_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if internet_destination_type is not None:
            self._values["internet_destination_type"] = internet_destination_type

    @builtins.property
    def destination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#destination DataDatabricksAccountNetworkPolicy#destination}.'''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def internet_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#internet_destination_type DataDatabricksAccountNetworkPolicy#internet_destination_type}.'''
        result = self._values.get("internet_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a91c2a77731341afff110152ffec51fb3545782b73072b270048159d1a990b77)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed769b64930170f47f641d2d5ef73bab76672d0b026a0507d0119df413887e7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b7f276e322b30a3cd08f0b541941b4573ef29421e404b07affe06efb958661)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb874ce9caa2b3d1aedc62b49e8cf9e73c01889e07bc541166aed7c8192c201a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__35f3b901fbe584024077b9ad9847b97171d4ed7e5e0843bdedd6f9e2c79d90e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7def637a63e3d8969f178d25a07e26a1f6309b198b9775d68274c03ecc4a113)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54dc8b9a2df0ef397e19cbbe608e94bc82163feba5db1a32e277bef324d6589d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetInternetDestinationType")
    def reset_internet_destination_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternetDestinationType", []))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="internetDestinationTypeInput")
    def internet_destination_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "internetDestinationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0957a38741cbcabd9bd61f7d99b9b404884022f462bae4e2a71346e2aee3ed11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internetDestinationType")
    def internet_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internetDestinationType"))

    @internet_destination_type.setter
    def internet_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a738e567a9046ab4243e6050a44d273e1cfab9646bc6618bb3852d669097529)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internetDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c01720b82e8c5bc386ea40a0433212fe7cb29db5e8fd68217627acb1f580cd1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "azure_storage_account": "azureStorageAccount",
        "azure_storage_service": "azureStorageService",
        "bucket_name": "bucketName",
        "region": "region",
        "storage_destination_type": "storageDestinationType",
    },
)
class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations:
    def __init__(
        self,
        *,
        azure_storage_account: typing.Optional[builtins.str] = None,
        azure_storage_service: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        storage_destination_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param azure_storage_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#azure_storage_account DataDatabricksAccountNetworkPolicy#azure_storage_account}.
        :param azure_storage_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#azure_storage_service DataDatabricksAccountNetworkPolicy#azure_storage_service}.
        :param bucket_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#bucket_name DataDatabricksAccountNetworkPolicy#bucket_name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#region DataDatabricksAccountNetworkPolicy#region}.
        :param storage_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#storage_destination_type DataDatabricksAccountNetworkPolicy#storage_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38593907ad79a4361edf642f9c560f3273306b71deb949a4cb9dc3768ab0606e)
            check_type(argname="argument azure_storage_account", value=azure_storage_account, expected_type=type_hints["azure_storage_account"])
            check_type(argname="argument azure_storage_service", value=azure_storage_service, expected_type=type_hints["azure_storage_service"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument storage_destination_type", value=storage_destination_type, expected_type=type_hints["storage_destination_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if azure_storage_account is not None:
            self._values["azure_storage_account"] = azure_storage_account
        if azure_storage_service is not None:
            self._values["azure_storage_service"] = azure_storage_service
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if region is not None:
            self._values["region"] = region
        if storage_destination_type is not None:
            self._values["storage_destination_type"] = storage_destination_type

    @builtins.property
    def azure_storage_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#azure_storage_account DataDatabricksAccountNetworkPolicy#azure_storage_account}.'''
        result = self._values.get("azure_storage_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#azure_storage_service DataDatabricksAccountNetworkPolicy#azure_storage_service}.'''
        result = self._values.get("azure_storage_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#bucket_name DataDatabricksAccountNetworkPolicy#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#region DataDatabricksAccountNetworkPolicy#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#storage_destination_type DataDatabricksAccountNetworkPolicy#storage_destination_type}.'''
        result = self._values.get("storage_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1067aa1854c96401c4804a403ce5b2db14a54bdbc7f5941815ab41e5477b0168)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4435f9e8e636889223b76294e785dea7e005e98d3a280d4b24d8143f5d5e9b1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1ef73c8e77f4018a7497593bcad8141289fef52d3f62711d2bf886d1fe2f635)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f1b36ef9144d29cef6f7c87d234df11d6e5d580bec8058ac03fffc1f9ebbce7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd99153f64d9313264a646649c963f2d51556c453649419844ef35d340575c6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6051d2f4d4cb13984d486dba176e878aeea1c11c5fdda780116da91c9a07ab48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf4e7ff5c4094f60ffe777307d392e0721306b237d58eb8c592c4de68617a9bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAzureStorageAccount")
    def reset_azure_storage_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageAccount", []))

    @jsii.member(jsii_name="resetAzureStorageService")
    def reset_azure_storage_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageService", []))

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetStorageDestinationType")
    def reset_storage_destination_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageDestinationType", []))

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccountInput")
    def azure_storage_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageServiceInput")
    def azure_storage_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="storageDestinationTypeInput")
    def storage_destination_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageDestinationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccount")
    def azure_storage_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageAccount"))

    @azure_storage_account.setter
    def azure_storage_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ed88862611f670d45a34297b973b40057969ec7a60dfb0469465571dfda9b80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageService")
    def azure_storage_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageService"))

    @azure_storage_service.setter
    def azure_storage_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__890274f182e45b634227d808a94d76b41480ef581ea90e2986f298ed3f538cf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb9540e3dd311825e4276588faf61077380a240f561d9643c763ad8681466b3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c22e52b4584ef3392473aa4eb161cd7759834fc3520b8c829711800b3de477d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageDestinationType")
    def storage_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageDestinationType"))

    @storage_destination_type.setter
    def storage_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16a446434e36c4479f32f19306fbcba21488ac58e5cc8a3db01f15032f7b0f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad982e4cc6d890331278d9340d2d624b689b3d0c0f5663c2cc59b454e429c2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8868d45cd62bdeb10db3d825ceac6a82b1f163d64f1736da19d61b55b50c0245)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAllowedInternetDestinations")
    def put_allowed_internet_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f98e8681fb5a46531b786725be565145cbfd08e98444ff0a1a276bad64bdf62c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedInternetDestinations", [value]))

    @jsii.member(jsii_name="putAllowedStorageDestinations")
    def put_allowed_storage_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62905669a0ee9d39d4bc555db53f0b67895fce497a2078d40b82bbb21f0f4542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedStorageDestinations", [value]))

    @jsii.member(jsii_name="putPolicyEnforcement")
    def put_policy_enforcement(
        self,
        *,
        dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforcement_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicy#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#enforcement_mode DataDatabricksAccountNetworkPolicy#enforcement_mode}.
        '''
        value = DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(
            dry_run_mode_product_filter=dry_run_mode_product_filter,
            enforcement_mode=enforcement_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyEnforcement", [value]))

    @jsii.member(jsii_name="resetAllowedInternetDestinations")
    def reset_allowed_internet_destinations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedInternetDestinations", []))

    @jsii.member(jsii_name="resetAllowedStorageDestinations")
    def reset_allowed_storage_destinations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedStorageDestinations", []))

    @jsii.member(jsii_name="resetPolicyEnforcement")
    def reset_policy_enforcement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyEnforcement", []))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinations")
    def allowed_internet_destinations(
        self,
    ) -> DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList:
        return typing.cast(DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList, jsii.get(self, "allowedInternetDestinations"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinations")
    def allowed_storage_destinations(
        self,
    ) -> DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList:
        return typing.cast(DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList, jsii.get(self, "allowedStorageDestinations"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcement")
    def policy_enforcement(
        self,
    ) -> "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference":
        return typing.cast("DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference", jsii.get(self, "policyEnforcement"))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinationsInput")
    def allowed_internet_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "allowedInternetDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinationsInput")
    def allowed_storage_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "allowedStorageDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcementInput")
    def policy_enforcement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]], jsii.get(self, "policyEnforcementInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictionModeInput")
    def restriction_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restrictionModeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictionMode")
    def restriction_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restrictionMode"))

    @restriction_mode.setter
    def restriction_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d8ccf5abbdb6a4f3fc4fbf70b70e6057f2b103a1d089a5599260687d04ac2ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ae3b57de146c03cf183f34798373c5b6d5cb86ea8cb69ff8c2d6a5c512b1e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement",
    jsii_struct_bases=[],
    name_mapping={
        "dry_run_mode_product_filter": "dryRunModeProductFilter",
        "enforcement_mode": "enforcementMode",
    },
)
class DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement:
    def __init__(
        self,
        *,
        dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforcement_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicy#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#enforcement_mode DataDatabricksAccountNetworkPolicy#enforcement_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a743a4809bfd403770aa409f017fba8ec7ae45f2c5aa5f96973523394d91c5a)
            check_type(argname="argument dry_run_mode_product_filter", value=dry_run_mode_product_filter, expected_type=type_hints["dry_run_mode_product_filter"])
            check_type(argname="argument enforcement_mode", value=enforcement_mode, expected_type=type_hints["enforcement_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dry_run_mode_product_filter is not None:
            self._values["dry_run_mode_product_filter"] = dry_run_mode_product_filter
        if enforcement_mode is not None:
            self._values["enforcement_mode"] = enforcement_mode

    @builtins.property
    def dry_run_mode_product_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicy#dry_run_mode_product_filter}.'''
        result = self._values.get("dry_run_mode_product_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enforcement_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#enforcement_mode DataDatabricksAccountNetworkPolicy#enforcement_mode}.'''
        result = self._values.get("enforcement_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__380d558af6224aabcd978676b6e411efcb2db92737b9e5361eb45a43cac302fd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDryRunModeProductFilter")
    def reset_dry_run_mode_product_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDryRunModeProductFilter", []))

    @jsii.member(jsii_name="resetEnforcementMode")
    def reset_enforcement_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforcementMode", []))

    @builtins.property
    @jsii.member(jsii_name="dryRunModeProductFilterInput")
    def dry_run_mode_product_filter_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dryRunModeProductFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="enforcementModeInput")
    def enforcement_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enforcementModeInput"))

    @builtins.property
    @jsii.member(jsii_name="dryRunModeProductFilter")
    def dry_run_mode_product_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dryRunModeProductFilter"))

    @dry_run_mode_product_filter.setter
    def dry_run_mode_product_filter(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa4af88529b6ef5790c94ac59140e83054bb6fe2646a43586c9c0929afc00d7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dryRunModeProductFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforcementMode")
    def enforcement_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforcementMode"))

    @enforcement_mode.setter
    def enforcement_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ddb54ad22fa0c54eb64279d68035cc116bc4abec372eccfd4f52ac6d9ee179)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforcementMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05095e725ae4f4ad5bf0c71ac754e0f73643ebdc869e4009116c0c9b8e94bc48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPolicyEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicy.DataDatabricksAccountNetworkPolicyEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__289db917eef67dbfef1a86395ed079d004083b94800ae37cd3b1c3ec42abea65)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworkAccess")
    def put_network_access(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#restriction_mode DataDatabricksAccountNetworkPolicy#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_internet_destinations DataDatabricksAccountNetworkPolicy#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#allowed_storage_destinations DataDatabricksAccountNetworkPolicy#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policy#policy_enforcement DataDatabricksAccountNetworkPolicy#policy_enforcement}.
        '''
        value = DataDatabricksAccountNetworkPolicyEgressNetworkAccess(
            restriction_mode=restriction_mode,
            allowed_internet_destinations=allowed_internet_destinations,
            allowed_storage_destinations=allowed_storage_destinations,
            policy_enforcement=policy_enforcement,
        )

        return typing.cast(None, jsii.invoke(self, "putNetworkAccess", [value]))

    @jsii.member(jsii_name="resetNetworkAccess")
    def reset_network_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkAccess", []))

    @builtins.property
    @jsii.member(jsii_name="networkAccess")
    def network_access(
        self,
    ) -> DataDatabricksAccountNetworkPolicyEgressNetworkAccessOutputReference:
        return typing.cast(DataDatabricksAccountNetworkPolicyEgressNetworkAccessOutputReference, jsii.get(self, "networkAccess"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessInput")
    def network_access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]], jsii.get(self, "networkAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgress]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgress]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b660fb4b9b78d0221085532c705f9e197cab576b0ac9afe839e5b5cbd733ddbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAccountNetworkPolicy",
    "DataDatabricksAccountNetworkPolicyConfig",
    "DataDatabricksAccountNetworkPolicyEgress",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccess",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessOutputReference",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement",
    "DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference",
    "DataDatabricksAccountNetworkPolicyEgressOutputReference",
]

publication.publish()

def _typecheckingstub__3aa916696b8a1f3d8c1e060d17d64385e407b1710f3fa9fa761d5b1587d8f2ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    egress: typing.Optional[typing.Union[DataDatabricksAccountNetworkPolicyEgress, typing.Dict[builtins.str, typing.Any]]] = None,
    network_policy_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b38ca795290007d91e09caf31410da69fd6354afb2fe24979a9f74eaf383791c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ac83a03b91c63cac183b696ab81ef56549bc8c673e09b231cadcede354a554(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ce35450ba90009f4864b91a6ddfd11ab40fd6efa3476dc0282a2b302f91df3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09aa6e9feddfae615244c3359fd4a38fbd830854743b96f6403b1bb139c5b215(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    egress: typing.Optional[typing.Union[DataDatabricksAccountNetworkPolicyEgress, typing.Dict[builtins.str, typing.Any]]] = None,
    network_policy_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7ec543ad23dbe2a8fded08872e30f67f7a736b3af223501ec0304e50778b14(
    *,
    network_access: typing.Optional[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccess, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca761b85c80c5b383d7913db907ffb0676bc6cc9a99ebd6c32bc8be283d9d9cc(
    *,
    restriction_mode: builtins.str,
    allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_enforcement: typing.Optional[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5800dc017d2e2f41e9bd6472ff2e7a95d9ac2b5bd93e544f664df69fc5c9124a(
    *,
    destination: typing.Optional[builtins.str] = None,
    internet_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a91c2a77731341afff110152ffec51fb3545782b73072b270048159d1a990b77(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed769b64930170f47f641d2d5ef73bab76672d0b026a0507d0119df413887e7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b7f276e322b30a3cd08f0b541941b4573ef29421e404b07affe06efb958661(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb874ce9caa2b3d1aedc62b49e8cf9e73c01889e07bc541166aed7c8192c201a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f3b901fbe584024077b9ad9847b97171d4ed7e5e0843bdedd6f9e2c79d90e3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7def637a63e3d8969f178d25a07e26a1f6309b198b9775d68274c03ecc4a113(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54dc8b9a2df0ef397e19cbbe608e94bc82163feba5db1a32e277bef324d6589d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0957a38741cbcabd9bd61f7d99b9b404884022f462bae4e2a71346e2aee3ed11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a738e567a9046ab4243e6050a44d273e1cfab9646bc6618bb3852d669097529(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c01720b82e8c5bc386ea40a0433212fe7cb29db5e8fd68217627acb1f580cd1e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38593907ad79a4361edf642f9c560f3273306b71deb949a4cb9dc3768ab0606e(
    *,
    azure_storage_account: typing.Optional[builtins.str] = None,
    azure_storage_service: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    storage_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1067aa1854c96401c4804a403ce5b2db14a54bdbc7f5941815ab41e5477b0168(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4435f9e8e636889223b76294e785dea7e005e98d3a280d4b24d8143f5d5e9b1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ef73c8e77f4018a7497593bcad8141289fef52d3f62711d2bf886d1fe2f635(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f1b36ef9144d29cef6f7c87d234df11d6e5d580bec8058ac03fffc1f9ebbce7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd99153f64d9313264a646649c963f2d51556c453649419844ef35d340575c6d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6051d2f4d4cb13984d486dba176e878aeea1c11c5fdda780116da91c9a07ab48(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf4e7ff5c4094f60ffe777307d392e0721306b237d58eb8c592c4de68617a9bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ed88862611f670d45a34297b973b40057969ec7a60dfb0469465571dfda9b80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890274f182e45b634227d808a94d76b41480ef581ea90e2986f298ed3f538cf1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb9540e3dd311825e4276588faf61077380a240f561d9643c763ad8681466b3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c22e52b4584ef3392473aa4eb161cd7759834fc3520b8c829711800b3de477d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a446434e36c4479f32f19306fbcba21488ac58e5cc8a3db01f15032f7b0f05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad982e4cc6d890331278d9340d2d624b689b3d0c0f5663c2cc59b454e429c2a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8868d45cd62bdeb10db3d825ceac6a82b1f163d64f1736da19d61b55b50c0245(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98e8681fb5a46531b786725be565145cbfd08e98444ff0a1a276bad64bdf62c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62905669a0ee9d39d4bc555db53f0b67895fce497a2078d40b82bbb21f0f4542(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d8ccf5abbdb6a4f3fc4fbf70b70e6057f2b103a1d089a5599260687d04ac2ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ae3b57de146c03cf183f34798373c5b6d5cb86ea8cb69ff8c2d6a5c512b1e0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a743a4809bfd403770aa409f017fba8ec7ae45f2c5aa5f96973523394d91c5a(
    *,
    dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    enforcement_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__380d558af6224aabcd978676b6e411efcb2db92737b9e5361eb45a43cac302fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4af88529b6ef5790c94ac59140e83054bb6fe2646a43586c9c0929afc00d7c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ddb54ad22fa0c54eb64279d68035cc116bc4abec372eccfd4f52ac6d9ee179(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05095e725ae4f4ad5bf0c71ac754e0f73643ebdc869e4009116c0c9b8e94bc48(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289db917eef67dbfef1a86395ed079d004083b94800ae37cd3b1c3ec42abea65(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b660fb4b9b78d0221085532c705f9e197cab576b0ac9afe839e5b5cbd733ddbb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPolicyEgress]],
) -> None:
    """Type checking stubs"""
    pass
