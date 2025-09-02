r'''
# `databricks_account_network_policy`

Refer to the Terraform Registry for docs: [`databricks_account_network_policy`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy).
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


class AccountNetworkPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy databricks_account_network_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        egress: typing.Optional[typing.Union["AccountNetworkPolicyEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        network_policy_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy databricks_account_network_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#account_id AccountNetworkPolicy#account_id}.
        :param egress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#egress AccountNetworkPolicy#egress}.
        :param network_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_policy_id AccountNetworkPolicy#network_policy_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d31bef16850e32e846680905a444a1e68e5b94f41b76f4db84eba88e6e777140)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AccountNetworkPolicyConfig(
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
        '''Generates CDKTF code for importing a AccountNetworkPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AccountNetworkPolicy to import.
        :param import_from_id: The id of the existing AccountNetworkPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AccountNetworkPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bd7039efeda4bcc0136936bf4d71fa2f6985d0d3c4cea483555f99138ec0e23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEgress")
    def put_egress(
        self,
        *,
        network_access: typing.Optional[typing.Union["AccountNetworkPolicyEgressNetworkAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_access AccountNetworkPolicy#network_access}.
        '''
        value = AccountNetworkPolicyEgress(network_access=network_access)

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
    def egress(self) -> "AccountNetworkPolicyEgressOutputReference":
        return typing.cast("AccountNetworkPolicyEgressOutputReference", jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="egressInput")
    def egress_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountNetworkPolicyEgress"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountNetworkPolicyEgress"]], jsii.get(self, "egressInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f6f316b4b1cfb0d077a9ceb08ebc4ba18d3d522948d6c280b7915e7b44fdb76f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkPolicyId")
    def network_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkPolicyId"))

    @network_policy_id.setter
    def network_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da04eb3a57943d166f849ff8d3b1f4cabfc7396f35e905abd9f83fb855e06a95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkPolicyId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyConfig",
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
class AccountNetworkPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        egress: typing.Optional[typing.Union["AccountNetworkPolicyEgress", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#account_id AccountNetworkPolicy#account_id}.
        :param egress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#egress AccountNetworkPolicy#egress}.
        :param network_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_policy_id AccountNetworkPolicy#network_policy_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(egress, dict):
            egress = AccountNetworkPolicyEgress(**egress)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0187c8f956c43d43141fe7fe8fdbe5fbcef3aa15dbe0b61a67332a21ebf873df)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#account_id AccountNetworkPolicy#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def egress(self) -> typing.Optional["AccountNetworkPolicyEgress"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#egress AccountNetworkPolicy#egress}.'''
        result = self._values.get("egress")
        return typing.cast(typing.Optional["AccountNetworkPolicyEgress"], result)

    @builtins.property
    def network_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_policy_id AccountNetworkPolicy#network_policy_id}.'''
        result = self._values.get("network_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgress",
    jsii_struct_bases=[],
    name_mapping={"network_access": "networkAccess"},
)
class AccountNetworkPolicyEgress:
    def __init__(
        self,
        *,
        network_access: typing.Optional[typing.Union["AccountNetworkPolicyEgressNetworkAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_access AccountNetworkPolicy#network_access}.
        '''
        if isinstance(network_access, dict):
            network_access = AccountNetworkPolicyEgressNetworkAccess(**network_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4733a0836ae56015f2f6fb48362348e7e6d05ed748dbd697f41856a8670c480)
            check_type(argname="argument network_access", value=network_access, expected_type=type_hints["network_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if network_access is not None:
            self._values["network_access"] = network_access

    @builtins.property
    def network_access(
        self,
    ) -> typing.Optional["AccountNetworkPolicyEgressNetworkAccess"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#network_access AccountNetworkPolicy#network_access}.'''
        result = self._values.get("network_access")
        return typing.cast(typing.Optional["AccountNetworkPolicyEgressNetworkAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccess",
    jsii_struct_bases=[],
    name_mapping={
        "restriction_mode": "restrictionMode",
        "allowed_internet_destinations": "allowedInternetDestinations",
        "allowed_storage_destinations": "allowedStorageDestinations",
        "policy_enforcement": "policyEnforcement",
    },
)
class AccountNetworkPolicyEgressNetworkAccess:
    def __init__(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union["AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#restriction_mode AccountNetworkPolicy#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_internet_destinations AccountNetworkPolicy#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_storage_destinations AccountNetworkPolicy#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#policy_enforcement AccountNetworkPolicy#policy_enforcement}.
        '''
        if isinstance(policy_enforcement, dict):
            policy_enforcement = AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(**policy_enforcement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c109db4525fa448c31e9a03798b52d49afa69d29dc973a1ed64d4c4cfef5ad27)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#restriction_mode AccountNetworkPolicy#restriction_mode}.'''
        result = self._values.get("restriction_mode")
        assert result is not None, "Required property 'restriction_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_internet_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_internet_destinations AccountNetworkPolicy#allowed_internet_destinations}.'''
        result = self._values.get("allowed_internet_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations"]]], result)

    @builtins.property
    def allowed_storage_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_storage_destinations AccountNetworkPolicy#allowed_storage_destinations}.'''
        result = self._values.get("allowed_storage_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations"]]], result)

    @builtins.property
    def policy_enforcement(
        self,
    ) -> typing.Optional["AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#policy_enforcement AccountNetworkPolicy#policy_enforcement}.'''
        result = self._values.get("policy_enforcement")
        return typing.cast(typing.Optional["AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyEgressNetworkAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "internet_destination_type": "internetDestinationType",
    },
)
class AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations:
    def __init__(
        self,
        *,
        destination: typing.Optional[builtins.str] = None,
        internet_destination_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#destination AccountNetworkPolicy#destination}.
        :param internet_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#internet_destination_type AccountNetworkPolicy#internet_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2694c1ab84ce4fde54bf15ce66f5d48731ce154a5e8dbd5497419efbcac8c1f1)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument internet_destination_type", value=internet_destination_type, expected_type=type_hints["internet_destination_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if internet_destination_type is not None:
            self._values["internet_destination_type"] = internet_destination_type

    @builtins.property
    def destination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#destination AccountNetworkPolicy#destination}.'''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def internet_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#internet_destination_type AccountNetworkPolicy#internet_destination_type}.'''
        result = self._values.get("internet_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61bc84f0258082d9d954c44830eb87b0f3584664365d2c824afc7e63133c9dda)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__354278122defa4c72c9066f32a90ff4a86b3e975acf7f6d5dea5be745acce55f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f59fcc386da866b95844b419c236ed50a547ae9f7b2dbace15301350b1c62c19)
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
            type_hints = typing.get_type_hints(_typecheckingstub__444a882b8a1bb30ac41e445d7c5c830f7e612276044d0511f104c24245fc15b0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac6c6ecd51c7e37ae073daf76201afeb7714f7a476d7b25a719b4b2a0b5dfee5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fdc364a1635365a95bcb139f9a66ea9b6f16da0679a232962b6f5ec0cea018d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fb617ec946464eeea32b528ca84f5b13aba6984247a380bc75346a42ae594ad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e10a0cfd0f95fb5bfb67601a91d6cd41f0372af372f8150ff9e8922ec8e5048)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internetDestinationType")
    def internet_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internetDestinationType"))

    @internet_destination_type.setter
    def internet_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888284ca2c4bcc67d601dc5e9876bedb7c1cd6f80b77ed9e5eb7bbdd7eb3849a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internetDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e20136dabdbe4035138bc5f96d70839a5a0c84537bb1a72bdb7c966898c932a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "azure_storage_account": "azureStorageAccount",
        "azure_storage_service": "azureStorageService",
        "bucket_name": "bucketName",
        "region": "region",
        "storage_destination_type": "storageDestinationType",
    },
)
class AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations:
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
        :param azure_storage_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#azure_storage_account AccountNetworkPolicy#azure_storage_account}.
        :param azure_storage_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#azure_storage_service AccountNetworkPolicy#azure_storage_service}.
        :param bucket_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#bucket_name AccountNetworkPolicy#bucket_name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#region AccountNetworkPolicy#region}.
        :param storage_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#storage_destination_type AccountNetworkPolicy#storage_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eabb5ce96adb126bc2df53b15ee99339ce57b3de607a6ce396730b086aca693c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#azure_storage_account AccountNetworkPolicy#azure_storage_account}.'''
        result = self._values.get("azure_storage_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#azure_storage_service AccountNetworkPolicy#azure_storage_service}.'''
        result = self._values.get("azure_storage_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#bucket_name AccountNetworkPolicy#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#region AccountNetworkPolicy#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#storage_destination_type AccountNetworkPolicy#storage_destination_type}.'''
        result = self._values.get("storage_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91ada93f3f0a79c24e0e2a57470e13d45e3a5df4831ab188d650c93630874716)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7023f7ab90b95c1fb4ae77641b562dad9843be10e5fd4c9f975e176845967f8e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33aa67ee2d5b2ff78c14ff49e255396752c2aebdae2c2e1f346d962680ef0072)
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
            type_hints = typing.get_type_hints(_typecheckingstub__91f3b504659971461392793ebb494a862a51c12ccbf5e302bebb098be5fe2b56)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d323aa25a0a0ee7c802a1e3349933971e8c453ae3c4462e1bfdf9577ae2f9f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f28aec82cd06749ea5579c2dc5fc4596c8a63e1b653eb9414a6afc4110eddc6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__facfa460b4836715360cc55db05d229bf1831c4961ead6b8ec139b3c9c8f5054)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e7c9e3b2bbda1e38d9dcf94267b13738f6a207c2d7443b5e028910685981f90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageService")
    def azure_storage_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageService"))

    @azure_storage_service.setter
    def azure_storage_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa9facdc64a4415078937198d78aded109fcfbb1e9f3fe90d3030bd98373c6bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4c2503f0501280b0a9579ffd4633ef5dbe5f7dcb93851e58fe71aa2ef919147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a373966ad878bcd01ef8163c965191de42bd04989caf2ceab1a7f04faab41558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageDestinationType")
    def storage_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageDestinationType"))

    @storage_destination_type.setter
    def storage_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce90db99ca62385ea0aaa2ae7cc43344ef35e04c9d82b5ac2c6fb8c67bd5a39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27a1358648c375bf3880611706ef62102d592131f134f2bbda6d4bbdf6731b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountNetworkPolicyEgressNetworkAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62df1bba51a93ef3ce58ca62f01b59181a0cbde9036c4bc4a66bc5d3be5b9b6d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAllowedInternetDestinations")
    def put_allowed_internet_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3693628c49456608a1af56c6ba1bbdfeccd6e8b8abf811df3c80f25104c410c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedInternetDestinations", [value]))

    @jsii.member(jsii_name="putAllowedStorageDestinations")
    def put_allowed_storage_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d41851da3d5c2d8480db5e942b9c299a5c1ae52a760c67cf8bb404ffbbe57738)
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
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#dry_run_mode_product_filter AccountNetworkPolicy#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#enforcement_mode AccountNetworkPolicy#enforcement_mode}.
        '''
        value = AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(
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
    ) -> AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList:
        return typing.cast(AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList, jsii.get(self, "allowedInternetDestinations"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinations")
    def allowed_storage_destinations(
        self,
    ) -> AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList:
        return typing.cast(AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList, jsii.get(self, "allowedStorageDestinations"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcement")
    def policy_enforcement(
        self,
    ) -> "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference":
        return typing.cast("AccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference", jsii.get(self, "policyEnforcement"))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinationsInput")
    def allowed_internet_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "allowedInternetDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinationsInput")
    def allowed_storage_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "allowedStorageDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcementInput")
    def policy_enforcement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement"]], jsii.get(self, "policyEnforcementInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c212c5be6407a51721db61548b691d909f4024b4fa3d286487ddc24b98047530)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__315f31603613a8a3ada4865d6416b94449561b9197cf9b7feff96237335c72ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement",
    jsii_struct_bases=[],
    name_mapping={
        "dry_run_mode_product_filter": "dryRunModeProductFilter",
        "enforcement_mode": "enforcementMode",
    },
)
class AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement:
    def __init__(
        self,
        *,
        dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforcement_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#dry_run_mode_product_filter AccountNetworkPolicy#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#enforcement_mode AccountNetworkPolicy#enforcement_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d4edef01807136e4ad1b80288ae2f9610ebe9c13f4b7d734f077e02d531c7d)
            check_type(argname="argument dry_run_mode_product_filter", value=dry_run_mode_product_filter, expected_type=type_hints["dry_run_mode_product_filter"])
            check_type(argname="argument enforcement_mode", value=enforcement_mode, expected_type=type_hints["enforcement_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dry_run_mode_product_filter is not None:
            self._values["dry_run_mode_product_filter"] = dry_run_mode_product_filter
        if enforcement_mode is not None:
            self._values["enforcement_mode"] = enforcement_mode

    @builtins.property
    def dry_run_mode_product_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#dry_run_mode_product_filter AccountNetworkPolicy#dry_run_mode_product_filter}.'''
        result = self._values.get("dry_run_mode_product_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enforcement_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#enforcement_mode AccountNetworkPolicy#enforcement_mode}.'''
        result = self._values.get("enforcement_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fa1bbd72c4b3d48afff30f62e1363a18b2befd0f97c06d0367323c6e55ab700)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a537054bef85b1d25722560e231e2bd6542421902bc1b24a6b43a4a6bf4ace35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dryRunModeProductFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforcementMode")
    def enforcement_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforcementMode"))

    @enforcement_mode.setter
    def enforcement_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__873661fe37e47b989754032e40dc5dbd55e1c176f776ab0fb8333bdbeb23dcd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforcementMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6136db59762905d95b0c80e69d0c9ad5ce36f1fe17b4ca2cda7dbdd2d3582a6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountNetworkPolicyEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountNetworkPolicy.AccountNetworkPolicyEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7e7f902fdb2fa5476b3344ea2cd4e59d58c6381fa79682fade15b4211b3ccf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworkAccess")
    def put_network_access(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union[AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#restriction_mode AccountNetworkPolicy#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_internet_destinations AccountNetworkPolicy#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#allowed_storage_destinations AccountNetworkPolicy#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_network_policy#policy_enforcement AccountNetworkPolicy#policy_enforcement}.
        '''
        value = AccountNetworkPolicyEgressNetworkAccess(
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
    def network_access(self) -> AccountNetworkPolicyEgressNetworkAccessOutputReference:
        return typing.cast(AccountNetworkPolicyEgressNetworkAccessOutputReference, jsii.get(self, "networkAccess"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessInput")
    def network_access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]], jsii.get(self, "networkAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgress]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgress]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa06d3905d8c0c987c5bca96fa07938b46210d939e00b696551e3eba7f36a54c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AccountNetworkPolicy",
    "AccountNetworkPolicyConfig",
    "AccountNetworkPolicyEgress",
    "AccountNetworkPolicyEgressNetworkAccess",
    "AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations",
    "AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsList",
    "AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinationsOutputReference",
    "AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations",
    "AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsList",
    "AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinationsOutputReference",
    "AccountNetworkPolicyEgressNetworkAccessOutputReference",
    "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement",
    "AccountNetworkPolicyEgressNetworkAccessPolicyEnforcementOutputReference",
    "AccountNetworkPolicyEgressOutputReference",
]

publication.publish()

def _typecheckingstub__d31bef16850e32e846680905a444a1e68e5b94f41b76f4db84eba88e6e777140(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    egress: typing.Optional[typing.Union[AccountNetworkPolicyEgress, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__0bd7039efeda4bcc0136936bf4d71fa2f6985d0d3c4cea483555f99138ec0e23(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f316b4b1cfb0d077a9ceb08ebc4ba18d3d522948d6c280b7915e7b44fdb76f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da04eb3a57943d166f849ff8d3b1f4cabfc7396f35e905abd9f83fb855e06a95(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0187c8f956c43d43141fe7fe8fdbe5fbcef3aa15dbe0b61a67332a21ebf873df(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: typing.Optional[builtins.str] = None,
    egress: typing.Optional[typing.Union[AccountNetworkPolicyEgress, typing.Dict[builtins.str, typing.Any]]] = None,
    network_policy_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4733a0836ae56015f2f6fb48362348e7e6d05ed748dbd697f41856a8670c480(
    *,
    network_access: typing.Optional[typing.Union[AccountNetworkPolicyEgressNetworkAccess, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c109db4525fa448c31e9a03798b52d49afa69d29dc973a1ed64d4c4cfef5ad27(
    *,
    restriction_mode: builtins.str,
    allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_enforcement: typing.Optional[typing.Union[AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2694c1ab84ce4fde54bf15ce66f5d48731ce154a5e8dbd5497419efbcac8c1f1(
    *,
    destination: typing.Optional[builtins.str] = None,
    internet_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61bc84f0258082d9d954c44830eb87b0f3584664365d2c824afc7e63133c9dda(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__354278122defa4c72c9066f32a90ff4a86b3e975acf7f6d5dea5be745acce55f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f59fcc386da866b95844b419c236ed50a547ae9f7b2dbace15301350b1c62c19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__444a882b8a1bb30ac41e445d7c5c830f7e612276044d0511f104c24245fc15b0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac6c6ecd51c7e37ae073daf76201afeb7714f7a476d7b25a719b4b2a0b5dfee5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fdc364a1635365a95bcb139f9a66ea9b6f16da0679a232962b6f5ec0cea018d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb617ec946464eeea32b528ca84f5b13aba6984247a380bc75346a42ae594ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e10a0cfd0f95fb5bfb67601a91d6cd41f0372af372f8150ff9e8922ec8e5048(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888284ca2c4bcc67d601dc5e9876bedb7c1cd6f80b77ed9e5eb7bbdd7eb3849a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20136dabdbe4035138bc5f96d70839a5a0c84537bb1a72bdb7c966898c932a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eabb5ce96adb126bc2df53b15ee99339ce57b3de607a6ce396730b086aca693c(
    *,
    azure_storage_account: typing.Optional[builtins.str] = None,
    azure_storage_service: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    storage_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ada93f3f0a79c24e0e2a57470e13d45e3a5df4831ab188d650c93630874716(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7023f7ab90b95c1fb4ae77641b562dad9843be10e5fd4c9f975e176845967f8e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33aa67ee2d5b2ff78c14ff49e255396752c2aebdae2c2e1f346d962680ef0072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f3b504659971461392793ebb494a862a51c12ccbf5e302bebb098be5fe2b56(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d323aa25a0a0ee7c802a1e3349933971e8c453ae3c4462e1bfdf9577ae2f9f9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f28aec82cd06749ea5579c2dc5fc4596c8a63e1b653eb9414a6afc4110eddc6b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__facfa460b4836715360cc55db05d229bf1831c4961ead6b8ec139b3c9c8f5054(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e7c9e3b2bbda1e38d9dcf94267b13738f6a207c2d7443b5e028910685981f90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa9facdc64a4415078937198d78aded109fcfbb1e9f3fe90d3030bd98373c6bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4c2503f0501280b0a9579ffd4633ef5dbe5f7dcb93851e58fe71aa2ef919147(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a373966ad878bcd01ef8163c965191de42bd04989caf2ceab1a7f04faab41558(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce90db99ca62385ea0aaa2ae7cc43344ef35e04c9d82b5ac2c6fb8c67bd5a39e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a1358648c375bf3880611706ef62102d592131f134f2bbda6d4bbdf6731b7d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62df1bba51a93ef3ce58ca62f01b59181a0cbde9036c4bc4a66bc5d3be5b9b6d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3693628c49456608a1af56c6ba1bbdfeccd6e8b8abf811df3c80f25104c410c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d41851da3d5c2d8480db5e942b9c299a5c1ae52a760c67cf8bb404ffbbe57738(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AccountNetworkPolicyEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c212c5be6407a51721db61548b691d909f4024b4fa3d286487ddc24b98047530(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__315f31603613a8a3ada4865d6416b94449561b9197cf9b7feff96237335c72ac(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d4edef01807136e4ad1b80288ae2f9610ebe9c13f4b7d734f077e02d531c7d(
    *,
    dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    enforcement_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa1bbd72c4b3d48afff30f62e1363a18b2befd0f97c06d0367323c6e55ab700(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a537054bef85b1d25722560e231e2bd6542421902bc1b24a6b43a4a6bf4ace35(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__873661fe37e47b989754032e40dc5dbd55e1c176f776ab0fb8333bdbeb23dcd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6136db59762905d95b0c80e69d0c9ad5ce36f1fe17b4ca2cda7dbdd2d3582a6b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgressNetworkAccessPolicyEnforcement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7e7f902fdb2fa5476b3344ea2cd4e59d58c6381fa79682fade15b4211b3ccf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa06d3905d8c0c987c5bca96fa07938b46210d939e00b696551e3eba7f36a54c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountNetworkPolicyEgress]],
) -> None:
    """Type checking stubs"""
    pass
