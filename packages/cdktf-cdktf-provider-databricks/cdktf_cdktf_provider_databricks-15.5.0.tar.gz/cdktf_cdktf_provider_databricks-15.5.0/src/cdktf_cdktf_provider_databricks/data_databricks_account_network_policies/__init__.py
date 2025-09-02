r'''
# `data_databricks_account_network_policies`

Refer to the Terraform Registry for docs: [`data_databricks_account_network_policies`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies).
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


class DataDatabricksAccountNetworkPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies databricks_account_network_policies}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies databricks_account_network_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68db3f644a5b43b9f6f1709f1a05b6daa9e5298aee64bc8fa23e14806fd8ff41)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAccountNetworkPoliciesConfig(
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
        '''Generates CDKTF code for importing a DataDatabricksAccountNetworkPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAccountNetworkPolicies to import.
        :param import_from_id: The id of the existing DataDatabricksAccountNetworkPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAccountNetworkPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdfe5a83488d3c3f1a84610283bae72aced72010ca0c3a7521b4d15e93b519b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="items")
    def items(self) -> "DataDatabricksAccountNetworkPoliciesItemsList":
        return typing.cast("DataDatabricksAccountNetworkPoliciesItemsList", jsii.get(self, "items"))


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
    },
)
class DataDatabricksAccountNetworkPoliciesConfig(
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
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__091b024f44e5504e0e6bae11dcaced344592674f157e7433de8c6056974fecdc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItems",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "egress": "egress",
        "network_policy_id": "networkPolicyId",
    },
)
class DataDatabricksAccountNetworkPoliciesItems:
    def __init__(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        egress: typing.Optional[typing.Union["DataDatabricksAccountNetworkPoliciesItemsEgress", typing.Dict[builtins.str, typing.Any]]] = None,
        network_policy_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#account_id DataDatabricksAccountNetworkPolicies#account_id}.
        :param egress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#egress DataDatabricksAccountNetworkPolicies#egress}.
        :param network_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#network_policy_id DataDatabricksAccountNetworkPolicies#network_policy_id}.
        '''
        if isinstance(egress, dict):
            egress = DataDatabricksAccountNetworkPoliciesItemsEgress(**egress)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23dee6fcdebdb84ce0e5ee74e584d7445c654e1419c609f5f71fb57fc204cb7d)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument egress", value=egress, expected_type=type_hints["egress"])
            check_type(argname="argument network_policy_id", value=network_policy_id, expected_type=type_hints["network_policy_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account_id is not None:
            self._values["account_id"] = account_id
        if egress is not None:
            self._values["egress"] = egress
        if network_policy_id is not None:
            self._values["network_policy_id"] = network_policy_id

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#account_id DataDatabricksAccountNetworkPolicies#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def egress(
        self,
    ) -> typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgress"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#egress DataDatabricksAccountNetworkPolicies#egress}.'''
        result = self._values.get("egress")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgress"], result)

    @builtins.property
    def network_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#network_policy_id DataDatabricksAccountNetworkPolicies#network_policy_id}.'''
        result = self._values.get("network_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgress",
    jsii_struct_bases=[],
    name_mapping={"network_access": "networkAccess"},
)
class DataDatabricksAccountNetworkPoliciesItemsEgress:
    def __init__(
        self,
        *,
        network_access: typing.Optional[typing.Union["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#network_access DataDatabricksAccountNetworkPolicies#network_access}.
        '''
        if isinstance(network_access, dict):
            network_access = DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess(**network_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92d3df2e374056511f147eae98d202a403ce985fbc39088cf3f122c0ed6ce81)
            check_type(argname="argument network_access", value=network_access, expected_type=type_hints["network_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if network_access is not None:
            self._values["network_access"] = network_access

    @builtins.property
    def network_access(
        self,
    ) -> typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#network_access DataDatabricksAccountNetworkPolicies#network_access}.'''
        result = self._values.get("network_access")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItemsEgress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess",
    jsii_struct_bases=[],
    name_mapping={
        "restriction_mode": "restrictionMode",
        "allowed_internet_destinations": "allowedInternetDestinations",
        "allowed_storage_destinations": "allowedStorageDestinations",
        "policy_enforcement": "policyEnforcement",
    },
)
class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess:
    def __init__(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#restriction_mode DataDatabricksAccountNetworkPolicies#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_internet_destinations DataDatabricksAccountNetworkPolicies#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_storage_destinations DataDatabricksAccountNetworkPolicies#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#policy_enforcement DataDatabricksAccountNetworkPolicies#policy_enforcement}.
        '''
        if isinstance(policy_enforcement, dict):
            policy_enforcement = DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement(**policy_enforcement)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__564427cb60e76f532afeb845b88310660750240576b01beeaf09d38042aad1b8)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#restriction_mode DataDatabricksAccountNetworkPolicies#restriction_mode}.'''
        result = self._values.get("restriction_mode")
        assert result is not None, "Required property 'restriction_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_internet_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_internet_destinations DataDatabricksAccountNetworkPolicies#allowed_internet_destinations}.'''
        result = self._values.get("allowed_internet_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations"]]], result)

    @builtins.property
    def allowed_storage_destinations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_storage_destinations DataDatabricksAccountNetworkPolicies#allowed_storage_destinations}.'''
        result = self._values.get("allowed_storage_destinations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations"]]], result)

    @builtins.property
    def policy_enforcement(
        self,
    ) -> typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#policy_enforcement DataDatabricksAccountNetworkPolicies#policy_enforcement}.'''
        result = self._values.get("policy_enforcement")
        return typing.cast(typing.Optional["DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "internet_destination_type": "internetDestinationType",
    },
)
class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations:
    def __init__(
        self,
        *,
        destination: typing.Optional[builtins.str] = None,
        internet_destination_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#destination DataDatabricksAccountNetworkPolicies#destination}.
        :param internet_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#internet_destination_type DataDatabricksAccountNetworkPolicies#internet_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b90efc95543cf2826792d2e20ca2b34fb82829119b890c88d79d65353986db81)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument internet_destination_type", value=internet_destination_type, expected_type=type_hints["internet_destination_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if internet_destination_type is not None:
            self._values["internet_destination_type"] = internet_destination_type

    @builtins.property
    def destination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#destination DataDatabricksAccountNetworkPolicies#destination}.'''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def internet_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#internet_destination_type DataDatabricksAccountNetworkPolicies#internet_destination_type}.'''
        result = self._values.get("internet_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac14a63da3c40186558ff94e0e67cc6fe5d37a5c4fbe0fe633be8eb8207e577a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caefcc7343bc4ef810072aa00847f494378251e6273ff6132dd22095bde607f4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77ad2cfb5b42d6dada4f6ec5f490eba91abc9df52a22adc2ea87fd86952c9fa5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dfa9ea7860eada6c4d2c492a2bca7856d79fe28e082f65bdb71512cf29d4d0eb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b30f729909809ffc724c88f34d550112914be5e5b46d920dba68dc1db3f6821b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8ab6d5259854826e0d3ea215a1640ce71269df65d39152ea1a0e791cfd8a234)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3f67e5312cafb73e4f9f04bd26011a76a7b6f63767ce51d121d6310d0523907)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9d33fcd33cca5c88081797381a3297211c9544946ee9afc4a33c5176b6be0b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internetDestinationType")
    def internet_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internetDestinationType"))

    @internet_destination_type.setter
    def internet_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e9a10278baf83fa72a95ce5749e35a4dfc22789aea9630598f39ece4707d81d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internetDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7258ccb26f4ee3fe2f0dc6af4c7ab432f6dc191036cbc98ec1dff97406578ad8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations",
    jsii_struct_bases=[],
    name_mapping={
        "azure_storage_account": "azureStorageAccount",
        "azure_storage_service": "azureStorageService",
        "bucket_name": "bucketName",
        "region": "region",
        "storage_destination_type": "storageDestinationType",
    },
)
class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations:
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
        :param azure_storage_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#azure_storage_account DataDatabricksAccountNetworkPolicies#azure_storage_account}.
        :param azure_storage_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#azure_storage_service DataDatabricksAccountNetworkPolicies#azure_storage_service}.
        :param bucket_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#bucket_name DataDatabricksAccountNetworkPolicies#bucket_name}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#region DataDatabricksAccountNetworkPolicies#region}.
        :param storage_destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#storage_destination_type DataDatabricksAccountNetworkPolicies#storage_destination_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ed06d7e9359b948b213eaedbe3f05ebb371f911473692bcd251787364ebab3)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#azure_storage_account DataDatabricksAccountNetworkPolicies#azure_storage_account}.'''
        result = self._values.get("azure_storage_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#azure_storage_service DataDatabricksAccountNetworkPolicies#azure_storage_service}.'''
        result = self._values.get("azure_storage_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#bucket_name DataDatabricksAccountNetworkPolicies#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#region DataDatabricksAccountNetworkPolicies#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#storage_destination_type DataDatabricksAccountNetworkPolicies#storage_destination_type}.'''
        result = self._values.get("storage_destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__75cf542bf3172fa1ead6859b2156a732e9c6a55ac830487b14b4cbdcb778b7ad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99dda7fddbe12da71d9b4c87557d3f3b7967bc6d7656ae3f140719b7c8a12c9c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abac741a144832ce7835bbe021091d2d402d3c8188b391e4b2669a8b8ce7f913)
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
            type_hints = typing.get_type_hints(_typecheckingstub__616864d3f8c38858cc0a34c6041e87a7d58224bf7fc62f02684e0301358c96f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31dfdb450f4a8f900086c63d9b1af7f10a151c2d555d07eeab8681556ab2fa6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ab22f528dad45a929fc14a161cab5fcd121e3aba80e6502e09374887154efbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b24e3303d3fa819dd99aca4fca434e0ab4e9e746a7a9ee85cdeb981a35abdc0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__314439b51d7e7a794536102b0d69aa3fa349012ecbc28132d0634523b5d04fd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureStorageService")
    def azure_storage_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageService"))

    @azure_storage_service.setter
    def azure_storage_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9acb3f211ee8128793538c87691152e9042056276d3db08c53b5c6d02223141)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25242d174706dfc3afc0e81d3ef4680cc88b90c08596712a27d60bc036a2e557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69ca659103d4e6114cdf69c5e0e2db669336702f36cc06bfbc9424d3de67fc25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageDestinationType")
    def storage_destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageDestinationType"))

    @storage_destination_type.setter
    def storage_destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca95cf30f6f9dfa87b10e69931b8005cf301df67e73ebc141b44072f3401ce4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageDestinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b765ddb8402bad0a7de27a78cd22dcd9b7541575948f4cda5ae4e5c6e241ea02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79ddc636012471c02f4d5c6d4d774965aea26c6eb46ae3807f03df6b1403cacf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAllowedInternetDestinations")
    def put_allowed_internet_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__706473c6bb7281cd180821b1a844572bb1da1c14f7daf89219783bfe80c761c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedInternetDestinations", [value]))

    @jsii.member(jsii_name="putAllowedStorageDestinations")
    def put_allowed_storage_destinations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae44e3d5a481630f018ae41b804bd995b8313147e7a412ee8d4555434f20d33b)
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
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicies#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#enforcement_mode DataDatabricksAccountNetworkPolicies#enforcement_mode}.
        '''
        value = DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement(
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
    ) -> DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsList:
        return typing.cast(DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsList, jsii.get(self, "allowedInternetDestinations"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinations")
    def allowed_storage_destinations(
        self,
    ) -> DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsList:
        return typing.cast(DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsList, jsii.get(self, "allowedStorageDestinations"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcement")
    def policy_enforcement(
        self,
    ) -> "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcementOutputReference":
        return typing.cast("DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcementOutputReference", jsii.get(self, "policyEnforcement"))

    @builtins.property
    @jsii.member(jsii_name="allowedInternetDestinationsInput")
    def allowed_internet_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]], jsii.get(self, "allowedInternetDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedStorageDestinationsInput")
    def allowed_storage_destinations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]], jsii.get(self, "allowedStorageDestinationsInput"))

    @builtins.property
    @jsii.member(jsii_name="policyEnforcementInput")
    def policy_enforcement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement"]], jsii.get(self, "policyEnforcementInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__9db988132490859e21d08aaaabf89f13f33de018abe1e5e6889e4194266d1edc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec5204de65a98b5efd0235f9ace2caf61b86c2623c9399660e0ffebf39d833a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement",
    jsii_struct_bases=[],
    name_mapping={
        "dry_run_mode_product_filter": "dryRunModeProductFilter",
        "enforcement_mode": "enforcementMode",
    },
)
class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement:
    def __init__(
        self,
        *,
        dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        enforcement_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dry_run_mode_product_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicies#dry_run_mode_product_filter}.
        :param enforcement_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#enforcement_mode DataDatabricksAccountNetworkPolicies#enforcement_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c4158239cd35a4def1ddb7b64be2c9efd4db90ac59dd280fd45d3514760c170)
            check_type(argname="argument dry_run_mode_product_filter", value=dry_run_mode_product_filter, expected_type=type_hints["dry_run_mode_product_filter"])
            check_type(argname="argument enforcement_mode", value=enforcement_mode, expected_type=type_hints["enforcement_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dry_run_mode_product_filter is not None:
            self._values["dry_run_mode_product_filter"] = dry_run_mode_product_filter
        if enforcement_mode is not None:
            self._values["enforcement_mode"] = enforcement_mode

    @builtins.property
    def dry_run_mode_product_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#dry_run_mode_product_filter DataDatabricksAccountNetworkPolicies#dry_run_mode_product_filter}.'''
        result = self._values.get("dry_run_mode_product_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enforcement_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#enforcement_mode DataDatabricksAccountNetworkPolicies#enforcement_mode}.'''
        result = self._values.get("enforcement_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0513fddcc239bc1f9e6474def6d90c4e281b6a7b3555d1abb9f13c2444067b47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__87ebe45e07804620f903addcd7625ee471e4a75c1f85f8a88864ddcd0492c06c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dryRunModeProductFilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforcementMode")
    def enforcement_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enforcementMode"))

    @enforcement_mode.setter
    def enforcement_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d453a38f14fd3e138b30346bdea36d942f748747468dd456286924cfdd82e5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforcementMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f9ab688caaa7c6c87275c9b500f4c9ca1949a9de427b84b23689845e8010b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsEgressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsEgressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b7795bd9907af5d629e4dc8af496ed65ac2bad84281dc020d55fa2a9f4e0ad2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworkAccess")
    def put_network_access(
        self,
        *,
        restriction_mode: builtins.str,
        allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_enforcement: typing.Optional[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param restriction_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#restriction_mode DataDatabricksAccountNetworkPolicies#restriction_mode}.
        :param allowed_internet_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_internet_destinations DataDatabricksAccountNetworkPolicies#allowed_internet_destinations}.
        :param allowed_storage_destinations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#allowed_storage_destinations DataDatabricksAccountNetworkPolicies#allowed_storage_destinations}.
        :param policy_enforcement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#policy_enforcement DataDatabricksAccountNetworkPolicies#policy_enforcement}.
        '''
        value = DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess(
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
    ) -> DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessOutputReference:
        return typing.cast(DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessOutputReference, jsii.get(self, "networkAccess"))

    @builtins.property
    @jsii.member(jsii_name="networkAccessInput")
    def network_access_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]], jsii.get(self, "networkAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__380cadea54cb88caf9c2c97099fa68e7b15ce990b8ba7e031c2622d8de5752f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d93cd12ed7192be9817431e33e4e311d6c67f2382f01c7deaf08dd99b88f5cd1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAccountNetworkPoliciesItemsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1598c7ea9969a04f27e3a985348248d0a9b8f6242d47b427ebfb36bd34297a54)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAccountNetworkPoliciesItemsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29b592356f6cea7fd1ab12814beb9f1c9accb2175e34403f29f7bc99ba07e697)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9dd8bca2cfc3aea1fa90682227e37d83ec3a2ea697092a4723e90c5d8a7a4ab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__598ae755d269f37f2c7444429ff68a31ba9c12c36556d7e08b3f87b42c5ce24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItems]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItems]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItems]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b6c26537634f05bb3713a536727f18fa075f30e163a9b0d8912561afa51dff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountNetworkPoliciesItemsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountNetworkPolicies.DataDatabricksAccountNetworkPoliciesItemsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__900fd7007e41f9b4ed3e48cca074fc2d647807d89be58122b439ac762474b9e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putEgress")
    def put_egress(
        self,
        *,
        network_access: typing.Optional[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param network_access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_network_policies#network_access DataDatabricksAccountNetworkPolicies#network_access}.
        '''
        value = DataDatabricksAccountNetworkPoliciesItemsEgress(
            network_access=network_access
        )

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

    @builtins.property
    @jsii.member(jsii_name="egress")
    def egress(self) -> DataDatabricksAccountNetworkPoliciesItemsEgressOutputReference:
        return typing.cast(DataDatabricksAccountNetworkPoliciesItemsEgressOutputReference, jsii.get(self, "egress"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="egressInput")
    def egress_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]], jsii.get(self, "egressInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__37c365279d20b8425e0b19296290ec63ada62579960c806297dca3d4932f15eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkPolicyId")
    def network_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkPolicyId"))

    @network_policy_id.setter
    def network_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97727d1925f107f05b90255f07076a254e4799188f16ef5b4c1272624eda8b9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAccountNetworkPoliciesItems]:
        return typing.cast(typing.Optional[DataDatabricksAccountNetworkPoliciesItems], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAccountNetworkPoliciesItems],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6be68005f9ba23b9c4b9e6c4d6668f71d3e1e5b0ea2c298878baba9ce80e5bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAccountNetworkPolicies",
    "DataDatabricksAccountNetworkPoliciesConfig",
    "DataDatabricksAccountNetworkPoliciesItems",
    "DataDatabricksAccountNetworkPoliciesItemsEgress",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsList",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinationsOutputReference",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsList",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinationsOutputReference",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessOutputReference",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement",
    "DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcementOutputReference",
    "DataDatabricksAccountNetworkPoliciesItemsEgressOutputReference",
    "DataDatabricksAccountNetworkPoliciesItemsList",
    "DataDatabricksAccountNetworkPoliciesItemsOutputReference",
]

publication.publish()

def _typecheckingstub__68db3f644a5b43b9f6f1709f1a05b6daa9e5298aee64bc8fa23e14806fd8ff41(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
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

def _typecheckingstub__cdfe5a83488d3c3f1a84610283bae72aced72010ca0c3a7521b4d15e93b519b1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__091b024f44e5504e0e6bae11dcaced344592674f157e7433de8c6056974fecdc(
    *,
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

def _typecheckingstub__23dee6fcdebdb84ce0e5ee74e584d7445c654e1419c609f5f71fb57fc204cb7d(
    *,
    account_id: typing.Optional[builtins.str] = None,
    egress: typing.Optional[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgress, typing.Dict[builtins.str, typing.Any]]] = None,
    network_policy_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92d3df2e374056511f147eae98d202a403ce985fbc39088cf3f122c0ed6ce81(
    *,
    network_access: typing.Optional[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__564427cb60e76f532afeb845b88310660750240576b01beeaf09d38042aad1b8(
    *,
    restriction_mode: builtins.str,
    allowed_internet_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_storage_destinations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_enforcement: typing.Optional[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b90efc95543cf2826792d2e20ca2b34fb82829119b890c88d79d65353986db81(
    *,
    destination: typing.Optional[builtins.str] = None,
    internet_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac14a63da3c40186558ff94e0e67cc6fe5d37a5c4fbe0fe633be8eb8207e577a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caefcc7343bc4ef810072aa00847f494378251e6273ff6132dd22095bde607f4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77ad2cfb5b42d6dada4f6ec5f490eba91abc9df52a22adc2ea87fd86952c9fa5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfa9ea7860eada6c4d2c492a2bca7856d79fe28e082f65bdb71512cf29d4d0eb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b30f729909809ffc724c88f34d550112914be5e5b46d920dba68dc1db3f6821b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8ab6d5259854826e0d3ea215a1640ce71269df65d39152ea1a0e791cfd8a234(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3f67e5312cafb73e4f9f04bd26011a76a7b6f63767ce51d121d6310d0523907(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9d33fcd33cca5c88081797381a3297211c9544946ee9afc4a33c5176b6be0b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e9a10278baf83fa72a95ce5749e35a4dfc22789aea9630598f39ece4707d81d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7258ccb26f4ee3fe2f0dc6af4c7ab432f6dc191036cbc98ec1dff97406578ad8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ed06d7e9359b948b213eaedbe3f05ebb371f911473692bcd251787364ebab3(
    *,
    azure_storage_account: typing.Optional[builtins.str] = None,
    azure_storage_service: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    storage_destination_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75cf542bf3172fa1ead6859b2156a732e9c6a55ac830487b14b4cbdcb778b7ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99dda7fddbe12da71d9b4c87557d3f3b7967bc6d7656ae3f140719b7c8a12c9c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abac741a144832ce7835bbe021091d2d402d3c8188b391e4b2669a8b8ce7f913(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__616864d3f8c38858cc0a34c6041e87a7d58224bf7fc62f02684e0301358c96f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31dfdb450f4a8f900086c63d9b1af7f10a151c2d555d07eeab8681556ab2fa6a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ab22f528dad45a929fc14a161cab5fcd121e3aba80e6502e09374887154efbe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b24e3303d3fa819dd99aca4fca434e0ab4e9e746a7a9ee85cdeb981a35abdc0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__314439b51d7e7a794536102b0d69aa3fa349012ecbc28132d0634523b5d04fd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9acb3f211ee8128793538c87691152e9042056276d3db08c53b5c6d02223141(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25242d174706dfc3afc0e81d3ef4680cc88b90c08596712a27d60bc036a2e557(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69ca659103d4e6114cdf69c5e0e2db669336702f36cc06bfbc9424d3de67fc25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca95cf30f6f9dfa87b10e69931b8005cf301df67e73ebc141b44072f3401ce4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b765ddb8402bad0a7de27a78cd22dcd9b7541575948f4cda5ae4e5c6e241ea02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ddc636012471c02f4d5c6d4d774965aea26c6eb46ae3807f03df6b1403cacf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__706473c6bb7281cd180821b1a844572bb1da1c14f7daf89219783bfe80c761c5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedInternetDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae44e3d5a481630f018ae41b804bd995b8313147e7a412ee8d4555434f20d33b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessAllowedStorageDestinations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9db988132490859e21d08aaaabf89f13f33de018abe1e5e6889e4194266d1edc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec5204de65a98b5efd0235f9ace2caf61b86c2623c9399660e0ffebf39d833a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccess]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c4158239cd35a4def1ddb7b64be2c9efd4db90ac59dd280fd45d3514760c170(
    *,
    dry_run_mode_product_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    enforcement_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0513fddcc239bc1f9e6474def6d90c4e281b6a7b3555d1abb9f13c2444067b47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87ebe45e07804620f903addcd7625ee471e4a75c1f85f8a88864ddcd0492c06c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d453a38f14fd3e138b30346bdea36d942f748747468dd456286924cfdd82e5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f9ab688caaa7c6c87275c9b500f4c9ca1949a9de427b84b23689845e8010b6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgressNetworkAccessPolicyEnforcement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b7795bd9907af5d629e4dc8af496ed65ac2bad84281dc020d55fa2a9f4e0ad2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__380cadea54cb88caf9c2c97099fa68e7b15ce990b8ba7e031c2622d8de5752f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountNetworkPoliciesItemsEgress]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d93cd12ed7192be9817431e33e4e311d6c67f2382f01c7deaf08dd99b88f5cd1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1598c7ea9969a04f27e3a985348248d0a9b8f6242d47b427ebfb36bd34297a54(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29b592356f6cea7fd1ab12814beb9f1c9accb2175e34403f29f7bc99ba07e697(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9dd8bca2cfc3aea1fa90682227e37d83ec3a2ea697092a4723e90c5d8a7a4ab(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__598ae755d269f37f2c7444429ff68a31ba9c12c36556d7e08b3f87b42c5ce24c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b6c26537634f05bb3713a536727f18fa075f30e163a9b0d8912561afa51dff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAccountNetworkPoliciesItems]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__900fd7007e41f9b4ed3e48cca074fc2d647807d89be58122b439ac762474b9e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37c365279d20b8425e0b19296290ec63ada62579960c806297dca3d4932f15eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97727d1925f107f05b90255f07076a254e4799188f16ef5b4c1272624eda8b9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6be68005f9ba23b9c4b9e6c4d6668f71d3e1e5b0ea2c298878baba9ce80e5bc(
    value: typing.Optional[DataDatabricksAccountNetworkPoliciesItems],
) -> None:
    """Type checking stubs"""
    pass
