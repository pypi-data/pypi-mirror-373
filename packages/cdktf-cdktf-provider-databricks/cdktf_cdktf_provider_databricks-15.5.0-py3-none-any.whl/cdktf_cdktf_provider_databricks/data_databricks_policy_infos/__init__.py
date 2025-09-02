r'''
# `data_databricks_policy_infos`

Refer to the Terraform Registry for docs: [`data_databricks_policy_infos`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos).
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


class DataDatabricksPolicyInfos(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfos",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos databricks_policy_infos}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        on_securable_fullname: builtins.str,
        on_securable_type: builtins.str,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos databricks_policy_infos} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_fullname DataDatabricksPolicyInfos#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_type DataDatabricksPolicyInfos#on_securable_type}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#workspace_id DataDatabricksPolicyInfos#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b89ea3e89750e29ed71027f7528523ee8579a98ca40755de5343b0203f0d066)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksPolicyInfosConfig(
            on_securable_fullname=on_securable_fullname,
            on_securable_type=on_securable_type,
            workspace_id=workspace_id,
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
        '''Generates CDKTF code for importing a DataDatabricksPolicyInfos resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksPolicyInfos to import.
        :param import_from_id: The id of the existing DataDatabricksPolicyInfos that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksPolicyInfos to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a46226a97660550e69829bcd057cdca00f0631ce376b870b36bf6cb4d8dac068)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="policies")
    def policies(self) -> "DataDatabricksPolicyInfosPoliciesList":
        return typing.cast("DataDatabricksPolicyInfosPoliciesList", jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullnameInput")
    def on_securable_fullname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onSecurableFullnameInput"))

    @builtins.property
    @jsii.member(jsii_name="onSecurableTypeInput")
    def on_securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onSecurableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullname")
    def on_securable_fullname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableFullname"))

    @on_securable_fullname.setter
    def on_securable_fullname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57dbe742327751ec485f18b39ccfd33295fc274c0b6c902ae034fd7df698bc40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableFullname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableType")
    def on_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableType"))

    @on_securable_type.setter
    def on_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3771e1f13e574c0d42f263365221bc1bfcfe5fe6fb073d53eae5e560c5b00a38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e13df05a098c780a1e5bf3bfc8826613658a26cc2aabb502fb6379fa5f17907)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "on_securable_fullname": "onSecurableFullname",
        "on_securable_type": "onSecurableType",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksPolicyInfosConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        on_securable_fullname: builtins.str,
        on_securable_type: builtins.str,
        workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_fullname DataDatabricksPolicyInfos#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_type DataDatabricksPolicyInfos#on_securable_type}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#workspace_id DataDatabricksPolicyInfos#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab63cc7e907c7af7032cf1030ccf443052025119a898e8feaf7a0b4207be4f41)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument on_securable_fullname", value=on_securable_fullname, expected_type=type_hints["on_securable_fullname"])
            check_type(argname="argument on_securable_type", value=on_securable_type, expected_type=type_hints["on_securable_type"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "on_securable_fullname": on_securable_fullname,
            "on_securable_type": on_securable_type,
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
    def on_securable_fullname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_fullname DataDatabricksPolicyInfos#on_securable_fullname}.'''
        result = self._values.get("on_securable_fullname")
        assert result is not None, "Required property 'on_securable_fullname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_type DataDatabricksPolicyInfos#on_securable_type}.'''
        result = self._values.get("on_securable_type")
        assert result is not None, "Required property 'on_securable_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#workspace_id DataDatabricksPolicyInfos#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPolicies",
    jsii_struct_bases=[],
    name_mapping={
        "for_securable_type": "forSecurableType",
        "policy_type": "policyType",
        "to_principals": "toPrincipals",
        "column_mask": "columnMask",
        "comment": "comment",
        "except_principals": "exceptPrincipals",
        "match_columns": "matchColumns",
        "name": "name",
        "on_securable_fullname": "onSecurableFullname",
        "on_securable_type": "onSecurableType",
        "row_filter": "rowFilter",
        "when_condition": "whenCondition",
    },
)
class DataDatabricksPolicyInfosPolicies:
    def __init__(
        self,
        *,
        for_securable_type: builtins.str,
        policy_type: builtins.str,
        to_principals: typing.Sequence[builtins.str],
        column_mask: typing.Optional[typing.Union["DataDatabricksPolicyInfosPoliciesColumnMask", typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
        match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesMatchColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        on_securable_fullname: typing.Optional[builtins.str] = None,
        on_securable_type: typing.Optional[builtins.str] = None,
        row_filter: typing.Optional[typing.Union["DataDatabricksPolicyInfosPoliciesRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        when_condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param for_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#for_securable_type DataDatabricksPolicyInfos#for_securable_type}.
        :param policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#policy_type DataDatabricksPolicyInfos#policy_type}.
        :param to_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#to_principals DataDatabricksPolicyInfos#to_principals}.
        :param column_mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#column_mask DataDatabricksPolicyInfos#column_mask}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#comment DataDatabricksPolicyInfos#comment}.
        :param except_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#except_principals DataDatabricksPolicyInfos#except_principals}.
        :param match_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#match_columns DataDatabricksPolicyInfos#match_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#name DataDatabricksPolicyInfos#name}.
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_fullname DataDatabricksPolicyInfos#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_type DataDatabricksPolicyInfos#on_securable_type}.
        :param row_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#row_filter DataDatabricksPolicyInfos#row_filter}.
        :param when_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#when_condition DataDatabricksPolicyInfos#when_condition}.
        '''
        if isinstance(column_mask, dict):
            column_mask = DataDatabricksPolicyInfosPoliciesColumnMask(**column_mask)
        if isinstance(row_filter, dict):
            row_filter = DataDatabricksPolicyInfosPoliciesRowFilter(**row_filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52826f113df35251b0be549526a09648c6c6085945f6212b405dc4947879d889)
            check_type(argname="argument for_securable_type", value=for_securable_type, expected_type=type_hints["for_securable_type"])
            check_type(argname="argument policy_type", value=policy_type, expected_type=type_hints["policy_type"])
            check_type(argname="argument to_principals", value=to_principals, expected_type=type_hints["to_principals"])
            check_type(argname="argument column_mask", value=column_mask, expected_type=type_hints["column_mask"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument except_principals", value=except_principals, expected_type=type_hints["except_principals"])
            check_type(argname="argument match_columns", value=match_columns, expected_type=type_hints["match_columns"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument on_securable_fullname", value=on_securable_fullname, expected_type=type_hints["on_securable_fullname"])
            check_type(argname="argument on_securable_type", value=on_securable_type, expected_type=type_hints["on_securable_type"])
            check_type(argname="argument row_filter", value=row_filter, expected_type=type_hints["row_filter"])
            check_type(argname="argument when_condition", value=when_condition, expected_type=type_hints["when_condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "for_securable_type": for_securable_type,
            "policy_type": policy_type,
            "to_principals": to_principals,
        }
        if column_mask is not None:
            self._values["column_mask"] = column_mask
        if comment is not None:
            self._values["comment"] = comment
        if except_principals is not None:
            self._values["except_principals"] = except_principals
        if match_columns is not None:
            self._values["match_columns"] = match_columns
        if name is not None:
            self._values["name"] = name
        if on_securable_fullname is not None:
            self._values["on_securable_fullname"] = on_securable_fullname
        if on_securable_type is not None:
            self._values["on_securable_type"] = on_securable_type
        if row_filter is not None:
            self._values["row_filter"] = row_filter
        if when_condition is not None:
            self._values["when_condition"] = when_condition

    @builtins.property
    def for_securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#for_securable_type DataDatabricksPolicyInfos#for_securable_type}.'''
        result = self._values.get("for_securable_type")
        assert result is not None, "Required property 'for_securable_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#policy_type DataDatabricksPolicyInfos#policy_type}.'''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to_principals(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#to_principals DataDatabricksPolicyInfos#to_principals}.'''
        result = self._values.get("to_principals")
        assert result is not None, "Required property 'to_principals' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def column_mask(
        self,
    ) -> typing.Optional["DataDatabricksPolicyInfosPoliciesColumnMask"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#column_mask DataDatabricksPolicyInfos#column_mask}.'''
        result = self._values.get("column_mask")
        return typing.cast(typing.Optional["DataDatabricksPolicyInfosPoliciesColumnMask"], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#comment DataDatabricksPolicyInfos#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def except_principals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#except_principals DataDatabricksPolicyInfos#except_principals}.'''
        result = self._values.get("except_principals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def match_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesMatchColumns"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#match_columns DataDatabricksPolicyInfos#match_columns}.'''
        result = self._values.get("match_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesMatchColumns"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#name DataDatabricksPolicyInfos#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_fullname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_fullname DataDatabricksPolicyInfos#on_securable_fullname}.'''
        result = self._values.get("on_securable_fullname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_securable_type DataDatabricksPolicyInfos#on_securable_type}.'''
        result = self._values.get("on_securable_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def row_filter(
        self,
    ) -> typing.Optional["DataDatabricksPolicyInfosPoliciesRowFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#row_filter DataDatabricksPolicyInfos#row_filter}.'''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional["DataDatabricksPolicyInfosPoliciesRowFilter"], result)

    @builtins.property
    def when_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#when_condition DataDatabricksPolicyInfos#when_condition}.'''
        result = self._values.get("when_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesColumnMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "on_column": "onColumn",
        "using": "using",
    },
)
class DataDatabricksPolicyInfosPoliciesColumnMask:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        on_column: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_column DataDatabricksPolicyInfos#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__449115109824fd2efb3a14f31df7bfd06b742b2288ee6fb23e13da2b4d8bed9d)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument on_column", value=on_column, expected_type=type_hints["on_column"])
            check_type(argname="argument using", value=using, expected_type=type_hints["using"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
            "on_column": on_column,
        }
        if using is not None:
            self._values["using"] = using

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_column(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_column DataDatabricksPolicyInfos#on_column}.'''
        result = self._values.get("on_column")
        assert result is not None, "Required property 'on_column' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesColumnMaskUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesColumnMaskUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPoliciesColumnMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfosPoliciesColumnMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesColumnMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5df6502dd1619e16bb10502180aaa8547fef156e3edb85d8923aba4a48136db9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a2e082c0a054b06fa702fe852f95a5d4f8f255b2f6b66f8123d03d3795cf587)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "DataDatabricksPolicyInfosPoliciesColumnMaskUsingList":
        return typing.cast("DataDatabricksPolicyInfosPoliciesColumnMaskUsingList", jsii.get(self, "using"))

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="onColumnInput")
    def on_column_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onColumnInput"))

    @builtins.property
    @jsii.member(jsii_name="usingInput")
    def using_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesColumnMaskUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesColumnMaskUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d0c4e7dd66b0d6fd11488f38f01f08f6ce3665537f82b518d09d57deb790616)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onColumn")
    def on_column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onColumn"))

    @on_column.setter
    def on_column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__318147bb8fdead50787f28d763a0fc1ad079f9efd4794983905f8f3514886b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onColumn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fff631cd76cc489727f27e56e518515a20a8f6908b2da94c7bb2ecddf7d713fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesColumnMaskUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class DataDatabricksPolicyInfosPoliciesColumnMaskUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#constant DataDatabricksPolicyInfos#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88f85096ddf26e802847355fba8c47de78f81b0518ea3d9edf6ab5e98b1ff614)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#constant DataDatabricksPolicyInfos#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPoliciesColumnMaskUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfosPoliciesColumnMaskUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesColumnMaskUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e75d8f7b3b09045298afa1ccf699a811001620bfe83f72c8a71757dd6fc1a6bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfosPoliciesColumnMaskUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3573173bc8fbd1dab0703367cb933b9bc25913e1ee1c2eb567c2b44a2f44c2c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfosPoliciesColumnMaskUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2067d8968285f3414f049cda26f434576bdf2cd0b4267c00d178c81a4140803f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa9b9fbfe458c27bb3e989a54f29627146f6da42c166e93afb7f1df15f789097)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d9466822e1ef78e4111187356bd03438bf8d13b1a2635e62ca7993e6f396510)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesColumnMaskUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesColumnMaskUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesColumnMaskUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a05d03500818d8cab553df0d69c9fefa97a9cd29fac1ef00130a5ae9792a777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfosPoliciesColumnMaskUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesColumnMaskUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1123e97fe1aaebcf960d5ccd1807b0418f2fac00b97253a342a982f4b1748c0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetConstant")
    def reset_constant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConstant", []))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="constantInput")
    def constant_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "constantInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a65a3c9ba4e36c24147c247ff6272ff4a34ddb3018519c47672167a3ac12683b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb8f1b6797e6eaed160ce29302b11b25e572c1553bdce2bf8a2ac100faa4082a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMaskUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMaskUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMaskUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffe323412a72028f6256d59d8fef79ab82f041d9180a7bbb4fdb70633a60f579)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfosPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd7476a75b3d29bc5803666320eaaf039d4c74bc1ead513bfbb593ec94533591)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfosPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b514c07da755e6f50e8a78e3d65784626aa86972ecadf1b42c187eb2e19fb020)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfosPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f489d79b1373c1016addb1d07e66937610f6e32c8eeb7b6c11a6281d1a1936f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d0a8d06d0c09674f4e509082fe14ac9ce3bab0eed14df39ae9a5c9ed772da2d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6007984bc73d664540ca9aea2f0be2cc324f7ffb2cebdd53d5bf85c26184a5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2c250da8f9e555be9a3b1e7431fb49a7146bb19957b357e5eca6ae1bb681bcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesMatchColumns",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "condition": "condition"},
)
class DataDatabricksPolicyInfosPoliciesMatchColumns:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.
        :param condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#condition DataDatabricksPolicyInfos#condition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f349bfb2291eef5f02a9d55cb0347bab098392c37649b9c58dedc23896018e6)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#condition DataDatabricksPolicyInfos#condition}.'''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPoliciesMatchColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfosPoliciesMatchColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesMatchColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__099e9cb6f715325649bfb64c0c839ee849ae1fd8bd1100f252de95bc270fff0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfosPoliciesMatchColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b21d6b99e1271aee0223403a0423a8aedf8ba53348b0a306b0fd738886a374eb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfosPoliciesMatchColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b5e4708d8838f3f5bfc0feed33199b142e6003e1597c3eb03c719056b103f1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c55791f9f64943c8369ad57e0ad88a4ad772ffa282c5d4a0decf27008718e6f7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3278b5a18438429d4fca2620502298258e552e146f36faecc438d6086ae020ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fc48edbc356b33eb3f27c355b17434f02999738b8b84258c26bd4cbbab02c27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfosPoliciesMatchColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesMatchColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddee5b76315f60dc819019754e410a5a9dcef5fee00afbb69e66feb015d214d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3210d066260f15e93198d22324c40b752483e9753afb11f62b979ef3311b5069)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f1229c9a7ef1e42a20130b844f2201e298f41b349700990d4978dc948a2857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesMatchColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesMatchColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesMatchColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb4b3a90b5d55b63239b15b9febce5ec86ee402dbb2ca3bc3f0def41379be37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfosPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9c1434bfe56124cadbe2a68420f6921e77530b91fa20feaf9cbda19d16f56f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putColumnMask")
    def put_column_mask(
        self,
        *,
        function_name: builtins.str,
        on_column: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#on_column DataDatabricksPolicyInfos#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.
        '''
        value = DataDatabricksPolicyInfosPoliciesColumnMask(
            function_name=function_name, on_column=on_column, using=using
        )

        return typing.cast(None, jsii.invoke(self, "putColumnMask", [value]))

    @jsii.member(jsii_name="putMatchColumns")
    def put_match_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesMatchColumns, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d80d53a0e0edc35803e88799cd86207b5db8b447079f6a20133a00f00eada9d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatchColumns", [value]))

    @jsii.member(jsii_name="putRowFilter")
    def put_row_filter(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.
        '''
        value = DataDatabricksPolicyInfosPoliciesRowFilter(
            function_name=function_name, using=using
        )

        return typing.cast(None, jsii.invoke(self, "putRowFilter", [value]))

    @jsii.member(jsii_name="resetColumnMask")
    def reset_column_mask(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColumnMask", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetExceptPrincipals")
    def reset_except_principals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExceptPrincipals", []))

    @jsii.member(jsii_name="resetMatchColumns")
    def reset_match_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatchColumns", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOnSecurableFullname")
    def reset_on_securable_fullname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnSecurableFullname", []))

    @jsii.member(jsii_name="resetOnSecurableType")
    def reset_on_securable_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnSecurableType", []))

    @jsii.member(jsii_name="resetRowFilter")
    def reset_row_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRowFilter", []))

    @jsii.member(jsii_name="resetWhenCondition")
    def reset_when_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhenCondition", []))

    @builtins.property
    @jsii.member(jsii_name="columnMask")
    def column_mask(self) -> DataDatabricksPolicyInfosPoliciesColumnMaskOutputReference:
        return typing.cast(DataDatabricksPolicyInfosPoliciesColumnMaskOutputReference, jsii.get(self, "columnMask"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="matchColumns")
    def match_columns(self) -> DataDatabricksPolicyInfosPoliciesMatchColumnsList:
        return typing.cast(DataDatabricksPolicyInfosPoliciesMatchColumnsList, jsii.get(self, "matchColumns"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> "DataDatabricksPolicyInfosPoliciesRowFilterOutputReference":
        return typing.cast("DataDatabricksPolicyInfosPoliciesRowFilterOutputReference", jsii.get(self, "rowFilter"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @builtins.property
    @jsii.member(jsii_name="columnMaskInput")
    def column_mask_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]], jsii.get(self, "columnMaskInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="exceptPrincipalsInput")
    def except_principals_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exceptPrincipalsInput"))

    @builtins.property
    @jsii.member(jsii_name="forSecurableTypeInput")
    def for_securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forSecurableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="matchColumnsInput")
    def match_columns_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]], jsii.get(self, "matchColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullnameInput")
    def on_securable_fullname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onSecurableFullnameInput"))

    @builtins.property
    @jsii.member(jsii_name="onSecurableTypeInput")
    def on_securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onSecurableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="policyTypeInput")
    def policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="rowFilterInput")
    def row_filter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfosPoliciesRowFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfosPoliciesRowFilter"]], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="toPrincipalsInput")
    def to_principals_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "toPrincipalsInput"))

    @builtins.property
    @jsii.member(jsii_name="whenConditionInput")
    def when_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whenConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbada0dbb6c0fd9521e5946f028fff6a5f73d7be076d99526057b9f3e05bd2f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exceptPrincipals")
    def except_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exceptPrincipals"))

    @except_principals.setter
    def except_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6779a6a3ace1b85d5561100a7d5fea97d5dc1d6bb9b9654500c9f8dcad4da804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exceptPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forSecurableType")
    def for_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forSecurableType"))

    @for_securable_type.setter
    def for_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee3a4a77f57b18113b33de6d33de44fe37f569b4ed1c1ed5a2851a90471060da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__846cce625b11bbc347970347dd23baf0055da5e33f94c44929e47d7e92177baf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullname")
    def on_securable_fullname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableFullname"))

    @on_securable_fullname.setter
    def on_securable_fullname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e891a9cd22307e826ccacf1e8cbfc1fd9a671892d990350eed9b25fae04cc87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableFullname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableType")
    def on_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableType"))

    @on_securable_type.setter
    def on_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c60c6849051344fc904508ca8ccbee3adc8a48095cda9a8115d82163bd14367c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyType"))

    @policy_type.setter
    def policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ad2ee61b41441009d7176abfb7db718d4e92a632af0510519f5be6a3edc7145)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toPrincipals")
    def to_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "toPrincipals"))

    @to_principals.setter
    def to_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__341b84887e6d430f90124721e5c446953a56d8239159c7ed0474a46acd09904e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whenCondition")
    def when_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "whenCondition"))

    @when_condition.setter
    def when_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd2e65e60c91b3cdd83bfe89a6935787897508f7e828bb9bd9d214d88db0a660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whenCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksPolicyInfosPolicies]:
        return typing.cast(typing.Optional[DataDatabricksPolicyInfosPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksPolicyInfosPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c03fb6cee14dc0ae24d54fd0e6ffa89ead824c80a46de076fa437fdb802d5aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesRowFilter",
    jsii_struct_bases=[],
    name_mapping={"function_name": "functionName", "using": "using"},
)
class DataDatabricksPolicyInfosPoliciesRowFilter:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e6a4d76dbb1befeea354a3f86834a8b2ccf3b90637fedb791d177d7aded5be7)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using", value=using, expected_type=type_hints["using"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
        }
        if using is not None:
            self._values["using"] = using

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#function_name DataDatabricksPolicyInfos#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesRowFilterUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#using DataDatabricksPolicyInfos#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesRowFilterUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPoliciesRowFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfosPoliciesRowFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesRowFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56538d6ee397ab7d3d033086f4584b2948e8d469a7f5fb9577a033324e8d4079)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfosPoliciesRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab49a61a3a985cbbab149905e0d028c77d3bff9e0bed87d4c7cda1988bfae27e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "DataDatabricksPolicyInfosPoliciesRowFilterUsingList":
        return typing.cast("DataDatabricksPolicyInfosPoliciesRowFilterUsingList", jsii.get(self, "using"))

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="usingInput")
    def using_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesRowFilterUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfosPoliciesRowFilterUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92efb46788209d61e45e97089855120d9843f9a97dd9f7d4e91e9dd6b05c1a29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dcf47ed2f52274cd835886af9966d942145ecadf3baf275bc1626cc39b7a2d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesRowFilterUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class DataDatabricksPolicyInfosPoliciesRowFilterUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#constant DataDatabricksPolicyInfos#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42d189319c524df96bcdd1c3853d791c72b534b42926f414d32c249c08de1218)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#alias DataDatabricksPolicyInfos#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_infos#constant DataDatabricksPolicyInfos#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfosPoliciesRowFilterUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfosPoliciesRowFilterUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesRowFilterUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__731b2bb3b72ca194273c6e87917337064948afde301f59f5227e7ce5ae9b9898)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfosPoliciesRowFilterUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__411d3b97b205a501631fb2091eeafb704706b931a4dbb55dc0e6d92de467f1e0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfosPoliciesRowFilterUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bea1f8b445eb429f492419135242a5a0380b554f8084fb54a6e6983268605bf4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9daa098a3100cb1c123e347c64466efa2b199759b3341872eb11a0089724d43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cb5b61843c62418861da39478a5a63b2dd38acb32931a80e9ef697e84379ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesRowFilterUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesRowFilterUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesRowFilterUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1bd9e0a4b1f7993ab1401871971452517c9c5f9b0122c2e2e9825439700d28f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfosPoliciesRowFilterUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfos.DataDatabricksPolicyInfosPoliciesRowFilterUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fdc6f032388cd08fb7ce84b1bb0cad54cca6a85f2ae5d69980a0990c21c089c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetConstant")
    def reset_constant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConstant", []))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="constantInput")
    def constant_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "constantInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9acc842e17f8a930ce933dde0de4c66a1e2054e9d98ca165bce1b810f67e198e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e92b784813d6743a1eb9c4f64f4938bee822dc7fca4af2066974f15a2960bb14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilterUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilterUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilterUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f5b025ce3aa77350c523292641196df5128f184bc80c07e6f9456a062c94798)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksPolicyInfos",
    "DataDatabricksPolicyInfosConfig",
    "DataDatabricksPolicyInfosPolicies",
    "DataDatabricksPolicyInfosPoliciesColumnMask",
    "DataDatabricksPolicyInfosPoliciesColumnMaskOutputReference",
    "DataDatabricksPolicyInfosPoliciesColumnMaskUsing",
    "DataDatabricksPolicyInfosPoliciesColumnMaskUsingList",
    "DataDatabricksPolicyInfosPoliciesColumnMaskUsingOutputReference",
    "DataDatabricksPolicyInfosPoliciesList",
    "DataDatabricksPolicyInfosPoliciesMatchColumns",
    "DataDatabricksPolicyInfosPoliciesMatchColumnsList",
    "DataDatabricksPolicyInfosPoliciesMatchColumnsOutputReference",
    "DataDatabricksPolicyInfosPoliciesOutputReference",
    "DataDatabricksPolicyInfosPoliciesRowFilter",
    "DataDatabricksPolicyInfosPoliciesRowFilterOutputReference",
    "DataDatabricksPolicyInfosPoliciesRowFilterUsing",
    "DataDatabricksPolicyInfosPoliciesRowFilterUsingList",
    "DataDatabricksPolicyInfosPoliciesRowFilterUsingOutputReference",
]

publication.publish()

def _typecheckingstub__2b89ea3e89750e29ed71027f7528523ee8579a98ca40755de5343b0203f0d066(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    on_securable_fullname: builtins.str,
    on_securable_type: builtins.str,
    workspace_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a46226a97660550e69829bcd057cdca00f0631ce376b870b36bf6cb4d8dac068(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57dbe742327751ec485f18b39ccfd33295fc274c0b6c902ae034fd7df698bc40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3771e1f13e574c0d42f263365221bc1bfcfe5fe6fb073d53eae5e560c5b00a38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e13df05a098c780a1e5bf3bfc8826613658a26cc2aabb502fb6379fa5f17907(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab63cc7e907c7af7032cf1030ccf443052025119a898e8feaf7a0b4207be4f41(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    on_securable_fullname: builtins.str,
    on_securable_type: builtins.str,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52826f113df35251b0be549526a09648c6c6085945f6212b405dc4947879d889(
    *,
    for_securable_type: builtins.str,
    policy_type: builtins.str,
    to_principals: typing.Sequence[builtins.str],
    column_mask: typing.Optional[typing.Union[DataDatabricksPolicyInfosPoliciesColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
    match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesMatchColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    on_securable_fullname: typing.Optional[builtins.str] = None,
    on_securable_type: typing.Optional[builtins.str] = None,
    row_filter: typing.Optional[typing.Union[DataDatabricksPolicyInfosPoliciesRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    when_condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__449115109824fd2efb3a14f31df7bfd06b742b2288ee6fb23e13da2b4d8bed9d(
    *,
    function_name: builtins.str,
    on_column: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df6502dd1619e16bb10502180aaa8547fef156e3edb85d8923aba4a48136db9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a2e082c0a054b06fa702fe852f95a5d4f8f255b2f6b66f8123d03d3795cf587(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d0c4e7dd66b0d6fd11488f38f01f08f6ce3665537f82b518d09d57deb790616(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__318147bb8fdead50787f28d763a0fc1ad079f9efd4794983905f8f3514886b1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fff631cd76cc489727f27e56e518515a20a8f6908b2da94c7bb2ecddf7d713fb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88f85096ddf26e802847355fba8c47de78f81b0518ea3d9edf6ab5e98b1ff614(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e75d8f7b3b09045298afa1ccf699a811001620bfe83f72c8a71757dd6fc1a6bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3573173bc8fbd1dab0703367cb933b9bc25913e1ee1c2eb567c2b44a2f44c2c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2067d8968285f3414f049cda26f434576bdf2cd0b4267c00d178c81a4140803f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa9b9fbfe458c27bb3e989a54f29627146f6da42c166e93afb7f1df15f789097(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d9466822e1ef78e4111187356bd03438bf8d13b1a2635e62ca7993e6f396510(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a05d03500818d8cab553df0d69c9fefa97a9cd29fac1ef00130a5ae9792a777(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesColumnMaskUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1123e97fe1aaebcf960d5ccd1807b0418f2fac00b97253a342a982f4b1748c0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a65a3c9ba4e36c24147c247ff6272ff4a34ddb3018519c47672167a3ac12683b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8f1b6797e6eaed160ce29302b11b25e572c1553bdce2bf8a2ac100faa4082a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffe323412a72028f6256d59d8fef79ab82f041d9180a7bbb4fdb70633a60f579(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesColumnMaskUsing]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7476a75b3d29bc5803666320eaaf039d4c74bc1ead513bfbb593ec94533591(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b514c07da755e6f50e8a78e3d65784626aa86972ecadf1b42c187eb2e19fb020(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f489d79b1373c1016addb1d07e66937610f6e32c8eeb7b6c11a6281d1a1936f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0a8d06d0c09674f4e509082fe14ac9ce3bab0eed14df39ae9a5c9ed772da2d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6007984bc73d664540ca9aea2f0be2cc324f7ffb2cebdd53d5bf85c26184a5d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2c250da8f9e555be9a3b1e7431fb49a7146bb19957b357e5eca6ae1bb681bcb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f349bfb2291eef5f02a9d55cb0347bab098392c37649b9c58dedc23896018e6(
    *,
    alias: typing.Optional[builtins.str] = None,
    condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099e9cb6f715325649bfb64c0c839ee849ae1fd8bd1100f252de95bc270fff0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b21d6b99e1271aee0223403a0423a8aedf8ba53348b0a306b0fd738886a374eb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b5e4708d8838f3f5bfc0feed33199b142e6003e1597c3eb03c719056b103f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c55791f9f64943c8369ad57e0ad88a4ad772ffa282c5d4a0decf27008718e6f7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3278b5a18438429d4fca2620502298258e552e146f36faecc438d6086ae020ee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fc48edbc356b33eb3f27c355b17434f02999738b8b84258c26bd4cbbab02c27(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesMatchColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddee5b76315f60dc819019754e410a5a9dcef5fee00afbb69e66feb015d214d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3210d066260f15e93198d22324c40b752483e9753afb11f62b979ef3311b5069(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f1229c9a7ef1e42a20130b844f2201e298f41b349700990d4978dc948a2857(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb4b3a90b5d55b63239b15b9febce5ec86ee402dbb2ca3bc3f0def41379be37(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesMatchColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c1434bfe56124cadbe2a68420f6921e77530b91fa20feaf9cbda19d16f56f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d80d53a0e0edc35803e88799cd86207b5db8b447079f6a20133a00f00eada9d9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesMatchColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbada0dbb6c0fd9521e5946f028fff6a5f73d7be076d99526057b9f3e05bd2f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6779a6a3ace1b85d5561100a7d5fea97d5dc1d6bb9b9654500c9f8dcad4da804(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee3a4a77f57b18113b33de6d33de44fe37f569b4ed1c1ed5a2851a90471060da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__846cce625b11bbc347970347dd23baf0055da5e33f94c44929e47d7e92177baf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e891a9cd22307e826ccacf1e8cbfc1fd9a671892d990350eed9b25fae04cc87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c60c6849051344fc904508ca8ccbee3adc8a48095cda9a8115d82163bd14367c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ad2ee61b41441009d7176abfb7db718d4e92a632af0510519f5be6a3edc7145(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__341b84887e6d430f90124721e5c446953a56d8239159c7ed0474a46acd09904e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd2e65e60c91b3cdd83bfe89a6935787897508f7e828bb9bd9d214d88db0a660(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c03fb6cee14dc0ae24d54fd0e6ffa89ead824c80a46de076fa437fdb802d5aa(
    value: typing.Optional[DataDatabricksPolicyInfosPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e6a4d76dbb1befeea354a3f86834a8b2ccf3b90637fedb791d177d7aded5be7(
    *,
    function_name: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56538d6ee397ab7d3d033086f4584b2948e8d469a7f5fb9577a033324e8d4079(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab49a61a3a985cbbab149905e0d028c77d3bff9e0bed87d4c7cda1988bfae27e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfosPoliciesRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92efb46788209d61e45e97089855120d9843f9a97dd9f7d4e91e9dd6b05c1a29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dcf47ed2f52274cd835886af9966d942145ecadf3baf275bc1626cc39b7a2d8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42d189319c524df96bcdd1c3853d791c72b534b42926f414d32c249c08de1218(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731b2bb3b72ca194273c6e87917337064948afde301f59f5227e7ce5ae9b9898(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__411d3b97b205a501631fb2091eeafb704706b931a4dbb55dc0e6d92de467f1e0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bea1f8b445eb429f492419135242a5a0380b554f8084fb54a6e6983268605bf4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9daa098a3100cb1c123e347c64466efa2b199759b3341872eb11a0089724d43(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cb5b61843c62418861da39478a5a63b2dd38acb32931a80e9ef697e84379ef3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1bd9e0a4b1f7993ab1401871971452517c9c5f9b0122c2e2e9825439700d28f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfosPoliciesRowFilterUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fdc6f032388cd08fb7ce84b1bb0cad54cca6a85f2ae5d69980a0990c21c089c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9acc842e17f8a930ce933dde0de4c66a1e2054e9d98ca165bce1b810f67e198e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e92b784813d6743a1eb9c4f64f4938bee822dc7fca4af2066974f15a2960bb14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f5b025ce3aa77350c523292641196df5128f184bc80c07e6f9456a062c94798(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfosPoliciesRowFilterUsing]],
) -> None:
    """Type checking stubs"""
    pass
