r'''
# `databricks_policy_info`

Refer to the Terraform Registry for docs: [`databricks_policy_info`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info).
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


class PolicyInfo(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfo",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info databricks_policy_info}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        for_securable_type: builtins.str,
        policy_type: builtins.str,
        to_principals: typing.Sequence[builtins.str],
        column_mask: typing.Optional[typing.Union["PolicyInfoColumnMask", typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
        match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        on_securable_fullname: typing.Optional[builtins.str] = None,
        on_securable_type: typing.Optional[builtins.str] = None,
        row_filter: typing.Optional[typing.Union["PolicyInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        when_condition: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info databricks_policy_info} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param for_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#for_securable_type PolicyInfo#for_securable_type}.
        :param policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#policy_type PolicyInfo#policy_type}.
        :param to_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#to_principals PolicyInfo#to_principals}.
        :param column_mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#column_mask PolicyInfo#column_mask}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#comment PolicyInfo#comment}.
        :param except_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#except_principals PolicyInfo#except_principals}.
        :param match_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#match_columns PolicyInfo#match_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#name PolicyInfo#name}.
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_fullname PolicyInfo#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_type PolicyInfo#on_securable_type}.
        :param row_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#row_filter PolicyInfo#row_filter}.
        :param when_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#when_condition PolicyInfo#when_condition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#workspace_id PolicyInfo#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c975d0dead2ab3f7b1e317bb8b841169ee2f5a8f625d2209f9cd0637566bf0ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = PolicyInfoConfig(
            for_securable_type=for_securable_type,
            policy_type=policy_type,
            to_principals=to_principals,
            column_mask=column_mask,
            comment=comment,
            except_principals=except_principals,
            match_columns=match_columns,
            name=name,
            on_securable_fullname=on_securable_fullname,
            on_securable_type=on_securable_type,
            row_filter=row_filter,
            when_condition=when_condition,
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
        '''Generates CDKTF code for importing a PolicyInfo resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PolicyInfo to import.
        :param import_from_id: The id of the existing PolicyInfo that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PolicyInfo to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad24b63b28d48c318a78d11a8c3818caa16d3ee398b67b0ae901743a5cd8640f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putColumnMask")
    def put_column_mask(
        self,
        *,
        function_name: builtins.str,
        on_column: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_column PolicyInfo#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.
        '''
        value = PolicyInfoColumnMask(
            function_name=function_name, on_column=on_column, using=using
        )

        return typing.cast(None, jsii.invoke(self, "putColumnMask", [value]))

    @jsii.member(jsii_name="putMatchColumns")
    def put_match_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a071a121f4a2efa49d198f5cff038fee42086139cfb24a94ab5c10bab4e1a03d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatchColumns", [value]))

    @jsii.member(jsii_name="putRowFilter")
    def put_row_filter(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.
        '''
        value = PolicyInfoRowFilter(function_name=function_name, using=using)

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
    @jsii.member(jsii_name="columnMask")
    def column_mask(self) -> "PolicyInfoColumnMaskOutputReference":
        return typing.cast("PolicyInfoColumnMaskOutputReference", jsii.get(self, "columnMask"))

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
    def match_columns(self) -> "PolicyInfoMatchColumnsList":
        return typing.cast("PolicyInfoMatchColumnsList", jsii.get(self, "matchColumns"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> "PolicyInfoRowFilterOutputReference":
        return typing.cast("PolicyInfoRowFilterOutputReference", jsii.get(self, "rowFilter"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PolicyInfoColumnMask"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PolicyInfoColumnMask"]], jsii.get(self, "columnMaskInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoMatchColumns"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoMatchColumns"]]], jsii.get(self, "matchColumnsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PolicyInfoRowFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PolicyInfoRowFilter"]], jsii.get(self, "rowFilterInput"))

    @builtins.property
    @jsii.member(jsii_name="toPrincipalsInput")
    def to_principals_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "toPrincipalsInput"))

    @builtins.property
    @jsii.member(jsii_name="whenConditionInput")
    def when_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whenConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d4e977e83a7300bb544cb017ce9bd5500c6faa4db9dc42285564b2867043d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exceptPrincipals")
    def except_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exceptPrincipals"))

    @except_principals.setter
    def except_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9b5881e02e727faffbadac2cb24ce2f942159b72f06967ca0188d1ddeb9b414)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exceptPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forSecurableType")
    def for_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forSecurableType"))

    @for_securable_type.setter
    def for_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__203c233e6670f5bdd91a1f3aad536616c4ff2607a75393650f62b0d606bc14e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a75ef25681dfc18ef73c5e4884b9ed1bbecb8219526d812c7501d3d92ca0d856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullname")
    def on_securable_fullname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableFullname"))

    @on_securable_fullname.setter
    def on_securable_fullname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b8118d88f73178c7f3fd0c8b94ea87af018ba273b172a9e7d353bd26c337a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableFullname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableType")
    def on_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableType"))

    @on_securable_type.setter
    def on_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f8f99c43f77866ad248d2632ab34cc3162d9d50074e0311d9bb09ea208531d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyType"))

    @policy_type.setter
    def policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36fb14811f3dbb0c3ffabbdafb9ae44f01b06ec12a192281ce80a2d8eb911803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toPrincipals")
    def to_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "toPrincipals"))

    @to_principals.setter
    def to_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61fd20e03daabda85940aef8b3386e9e25a2bbe2ab8cb49af1970a496f39af9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whenCondition")
    def when_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "whenCondition"))

    @when_condition.setter
    def when_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9115642afcba7991abf412cfebd915036eaf831ca962c3f062cc1a190efdf9aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whenCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40e1b989dce8e837556515b5fa3d6bd7652f6da0b90c321bcc36eed823f307af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoColumnMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "on_column": "onColumn",
        "using": "using",
    },
)
class PolicyInfoColumnMask:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        on_column: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_column PolicyInfo#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f33bfa20c2cde2037c2472bbf628c771c847a2dbe8496dac9dd9acc3142cb36)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_column(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_column PolicyInfo#on_column}.'''
        result = self._values.get("on_column")
        assert result is not None, "Required property 'on_column' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoColumnMaskUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoColumnMaskUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoColumnMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PolicyInfoColumnMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoColumnMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20dc6aed7418e69470a9fcfe8b3afb3eb779a15857b2c439de192e8f2d0e87ec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1e5494a4f08c9e75af4c1871b5b9cd67f9d675eff6dc8ca047a583ca262640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "PolicyInfoColumnMaskUsingList":
        return typing.cast("PolicyInfoColumnMaskUsingList", jsii.get(self, "using"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoColumnMaskUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoColumnMaskUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__309cdf5540cd2d31bec68c64a75bc3fcb76495e983dac981e2c16b1b2df2f34a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onColumn")
    def on_column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onColumn"))

    @on_column.setter
    def on_column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62e0dcea198bddd9e81b4cbb3d2d602089ec2e8acd803bba093b185673e6043c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onColumn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b43fdda9b652b3bd195f3575207c1d0d11c4ae6867b092b651cd5ced99838e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoColumnMaskUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class PolicyInfoColumnMaskUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#constant PolicyInfo#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6815952419a7332255ecfc23e64dc42a96601f2bdae77764666246d227e16e11)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#constant PolicyInfo#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoColumnMaskUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PolicyInfoColumnMaskUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoColumnMaskUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfc51b57c4f75999cfd0e4111074403d1343062678fca730e654d125d6f7d17b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PolicyInfoColumnMaskUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f88095fe29cfa70fc9d4efc1de6765f09c543256b00f74f832f079a46434c96f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PolicyInfoColumnMaskUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c4b64df13f5227b5b936f856501e7f67def888f972b4d996a720d526182c3ed)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0b4482cc757ab74310b1ab981a111f39edf875cd61a6e49801f9dda91873ff8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__53753f94f440eba2b5b30ed48b78e58ec024b7184fa34b1640a1bcf7aa259f30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoColumnMaskUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoColumnMaskUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoColumnMaskUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59405d309c3b93cffcaf950b4e7a7f80fa72df18db9683415d735979609c802a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PolicyInfoColumnMaskUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoColumnMaskUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60808f2a4905d4503fe8b013c3b39c55c12943e9ca42f18ddbafe7839c0a4a81)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3822a513b6b24547e0df6a16b6caa20ff72c521953c86fbf0737830d8e0b2a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e39d12db9a838b54bcfeced4ea850af5a3770045f49ae7c40858d3dfc871780)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMaskUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMaskUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMaskUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__068c78edd334e54aa0cf2713ae876509a4a8c53a5c100562294ad4207ebaa857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
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
        "workspace_id": "workspaceId",
    },
)
class PolicyInfoConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        for_securable_type: builtins.str,
        policy_type: builtins.str,
        to_principals: typing.Sequence[builtins.str],
        column_mask: typing.Optional[typing.Union[PolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
        match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        on_securable_fullname: typing.Optional[builtins.str] = None,
        on_securable_type: typing.Optional[builtins.str] = None,
        row_filter: typing.Optional[typing.Union["PolicyInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
        when_condition: typing.Optional[builtins.str] = None,
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
        :param for_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#for_securable_type PolicyInfo#for_securable_type}.
        :param policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#policy_type PolicyInfo#policy_type}.
        :param to_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#to_principals PolicyInfo#to_principals}.
        :param column_mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#column_mask PolicyInfo#column_mask}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#comment PolicyInfo#comment}.
        :param except_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#except_principals PolicyInfo#except_principals}.
        :param match_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#match_columns PolicyInfo#match_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#name PolicyInfo#name}.
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_fullname PolicyInfo#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_type PolicyInfo#on_securable_type}.
        :param row_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#row_filter PolicyInfo#row_filter}.
        :param when_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#when_condition PolicyInfo#when_condition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#workspace_id PolicyInfo#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(column_mask, dict):
            column_mask = PolicyInfoColumnMask(**column_mask)
        if isinstance(row_filter, dict):
            row_filter = PolicyInfoRowFilter(**row_filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc30361cf56e8e683f0a3a9799b5474d3c10500c0993ddce381b6880e4489fc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "for_securable_type": for_securable_type,
            "policy_type": policy_type,
            "to_principals": to_principals,
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
    def for_securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#for_securable_type PolicyInfo#for_securable_type}.'''
        result = self._values.get("for_securable_type")
        assert result is not None, "Required property 'for_securable_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#policy_type PolicyInfo#policy_type}.'''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to_principals(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#to_principals PolicyInfo#to_principals}.'''
        result = self._values.get("to_principals")
        assert result is not None, "Required property 'to_principals' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def column_mask(self) -> typing.Optional[PolicyInfoColumnMask]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#column_mask PolicyInfo#column_mask}.'''
        result = self._values.get("column_mask")
        return typing.cast(typing.Optional[PolicyInfoColumnMask], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#comment PolicyInfo#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def except_principals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#except_principals PolicyInfo#except_principals}.'''
        result = self._values.get("except_principals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def match_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoMatchColumns"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#match_columns PolicyInfo#match_columns}.'''
        result = self._values.get("match_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoMatchColumns"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#name PolicyInfo#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_fullname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_fullname PolicyInfo#on_securable_fullname}.'''
        result = self._values.get("on_securable_fullname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#on_securable_type PolicyInfo#on_securable_type}.'''
        result = self._values.get("on_securable_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def row_filter(self) -> typing.Optional["PolicyInfoRowFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#row_filter PolicyInfo#row_filter}.'''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional["PolicyInfoRowFilter"], result)

    @builtins.property
    def when_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#when_condition PolicyInfo#when_condition}.'''
        result = self._values.get("when_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#workspace_id PolicyInfo#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoMatchColumns",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "condition": "condition"},
)
class PolicyInfoMatchColumns:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.
        :param condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#condition PolicyInfo#condition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__514a6b6e9cbf8e83f0c3c11b91d076ca3108d9f4cd98759033a8d417dbc22f97)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#condition PolicyInfo#condition}.'''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoMatchColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PolicyInfoMatchColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoMatchColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69da653970c2772be9f2f583fb93d6a8856f1c390cd6c89d5176d12da97f0b0c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PolicyInfoMatchColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b284a9361b9b0d1733d6714c5906b3721809b06acf979657c4bd52bea6eae6d1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PolicyInfoMatchColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c90993ce56c1031a58e4b985aec049c34595f14dae95188e74261a166bcb999)
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
            type_hints = typing.get_type_hints(_typecheckingstub__242e1283e2efc0b0ae13b185652d7829ab54b295e6d58c33d8d479c296bf2b00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4cc9547685875d4cf0a761189a21f106b774e3fcf64b36abbcb9e593e94c3d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoMatchColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoMatchColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoMatchColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c40ce891d208ebac88a1b34ef2717eb608efb854a438fca125f3f8051da4d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PolicyInfoMatchColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoMatchColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15743eb0153c7567f602f8a986085fba96284f99131f0e76df89ca33cdfa57a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__61b4e476754d91e3a24e33b2d3077730714214b229e1869f23a7aa309d36d455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__896f70a68c2a7a489d66f61441f30f957fd5156b6e46bc7c94235dd4b6b33cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoMatchColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoMatchColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoMatchColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b49ec4aa54706386ce4080464b967cf88015e561d74c8eb120e1785a1a9a57e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoRowFilter",
    jsii_struct_bases=[],
    name_mapping={"function_name": "functionName", "using": "using"},
)
class PolicyInfoRowFilter:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3187e37c839cb793d697e845df5f1b1900c082af2fa507e3a68b339c669c6589)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using", value=using, expected_type=type_hints["using"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
        }
        if using is not None:
            self._values["using"] = using

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#function_name PolicyInfo#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoRowFilterUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#using PolicyInfo#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoRowFilterUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoRowFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PolicyInfoRowFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoRowFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1c98b9fb6ecb41c47c16ade3e2b8bb25a65ca415d3ccba137bf165dec36e62a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511baecd919f32940a07dfcc424cffae0eade513c969910470d8bc6dccefc5b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "PolicyInfoRowFilterUsingList":
        return typing.cast("PolicyInfoRowFilterUsingList", jsii.get(self, "using"))

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="usingInput")
    def using_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoRowFilterUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PolicyInfoRowFilterUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0be7f86698198c78e1e8da7ad07e6c96fbeb40c47236d2b95580fe8f47555b4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd86e58643817a5efd76b4ff497b92c95c6cb54200e6c10b7aa6f80252808c56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoRowFilterUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class PolicyInfoRowFilterUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#constant PolicyInfo#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff6a70017a9ceee9bac5420a09ae0bb7069fc13475ef8bb073c39b9b1480a23)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#alias PolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/policy_info#constant PolicyInfo#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyInfoRowFilterUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PolicyInfoRowFilterUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoRowFilterUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fb55e7a7239f72e7a86a44af211af47dee99188758422d2cc78531d7eb10bbb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PolicyInfoRowFilterUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bb1cf468994580f2ffb54d9c838103fc494b86a25474862fcac37a76ca6390a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PolicyInfoRowFilterUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a47879dbf65f192636f0d7193824b884467f7d3320474d2b5528e6df660ef7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10536737c879006fd9dbc345be56620a1894460217e66559e86dc6e352e51bd0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00cac1eb3a26c630dbe514daec952cd21fbd7f32c23354ec9f53c8a12e50298b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoRowFilterUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoRowFilterUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoRowFilterUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__537924a1352df9fb7485ab3e9904e6b05c59d2d504a7a20b147d76e9c3a9d716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PolicyInfoRowFilterUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.policyInfo.PolicyInfoRowFilterUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__51c7a6c7d1652de360c7bfaa287060a179ed790deb3ddfba3b02b8dc945a0d57)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4d412a184b0914b0fe8f7713ddbd2a6f369989558273329ccc58a0d1557b434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f458b7ee60c49d0901d74cea7bd3c63b62a159dd7cb1476b51a5075678064a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilterUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilterUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilterUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b5e2c0458b3afcd701b08c9bcc330f86267bffb4678abc00b340900b5a9a398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PolicyInfo",
    "PolicyInfoColumnMask",
    "PolicyInfoColumnMaskOutputReference",
    "PolicyInfoColumnMaskUsing",
    "PolicyInfoColumnMaskUsingList",
    "PolicyInfoColumnMaskUsingOutputReference",
    "PolicyInfoConfig",
    "PolicyInfoMatchColumns",
    "PolicyInfoMatchColumnsList",
    "PolicyInfoMatchColumnsOutputReference",
    "PolicyInfoRowFilter",
    "PolicyInfoRowFilterOutputReference",
    "PolicyInfoRowFilterUsing",
    "PolicyInfoRowFilterUsingList",
    "PolicyInfoRowFilterUsingOutputReference",
]

publication.publish()

def _typecheckingstub__c975d0dead2ab3f7b1e317bb8b841169ee2f5a8f625d2209f9cd0637566bf0ab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    for_securable_type: builtins.str,
    policy_type: builtins.str,
    to_principals: typing.Sequence[builtins.str],
    column_mask: typing.Optional[typing.Union[PolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
    match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    on_securable_fullname: typing.Optional[builtins.str] = None,
    on_securable_type: typing.Optional[builtins.str] = None,
    row_filter: typing.Optional[typing.Union[PolicyInfoRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    when_condition: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ad24b63b28d48c318a78d11a8c3818caa16d3ee398b67b0ae901743a5cd8640f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a071a121f4a2efa49d198f5cff038fee42086139cfb24a94ab5c10bab4e1a03d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d4e977e83a7300bb544cb017ce9bd5500c6faa4db9dc42285564b2867043d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b5881e02e727faffbadac2cb24ce2f942159b72f06967ca0188d1ddeb9b414(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__203c233e6670f5bdd91a1f3aad536616c4ff2607a75393650f62b0d606bc14e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75ef25681dfc18ef73c5e4884b9ed1bbecb8219526d812c7501d3d92ca0d856(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b8118d88f73178c7f3fd0c8b94ea87af018ba273b172a9e7d353bd26c337a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f8f99c43f77866ad248d2632ab34cc3162d9d50074e0311d9bb09ea208531d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36fb14811f3dbb0c3ffabbdafb9ae44f01b06ec12a192281ce80a2d8eb911803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61fd20e03daabda85940aef8b3386e9e25a2bbe2ab8cb49af1970a496f39af9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9115642afcba7991abf412cfebd915036eaf831ca962c3f062cc1a190efdf9aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e1b989dce8e837556515b5fa3d6bd7652f6da0b90c321bcc36eed823f307af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f33bfa20c2cde2037c2472bbf628c771c847a2dbe8496dac9dd9acc3142cb36(
    *,
    function_name: builtins.str,
    on_column: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20dc6aed7418e69470a9fcfe8b3afb3eb779a15857b2c439de192e8f2d0e87ec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1e5494a4f08c9e75af4c1871b5b9cd67f9d675eff6dc8ca047a583ca262640(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__309cdf5540cd2d31bec68c64a75bc3fcb76495e983dac981e2c16b1b2df2f34a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62e0dcea198bddd9e81b4cbb3d2d602089ec2e8acd803bba093b185673e6043c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b43fdda9b652b3bd195f3575207c1d0d11c4ae6867b092b651cd5ced99838e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6815952419a7332255ecfc23e64dc42a96601f2bdae77764666246d227e16e11(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfc51b57c4f75999cfd0e4111074403d1343062678fca730e654d125d6f7d17b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88095fe29cfa70fc9d4efc1de6765f09c543256b00f74f832f079a46434c96f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c4b64df13f5227b5b936f856501e7f67def888f972b4d996a720d526182c3ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0b4482cc757ab74310b1ab981a111f39edf875cd61a6e49801f9dda91873ff8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53753f94f440eba2b5b30ed48b78e58ec024b7184fa34b1640a1bcf7aa259f30(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59405d309c3b93cffcaf950b4e7a7f80fa72df18db9683415d735979609c802a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoColumnMaskUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60808f2a4905d4503fe8b013c3b39c55c12943e9ca42f18ddbafe7839c0a4a81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3822a513b6b24547e0df6a16b6caa20ff72c521953c86fbf0737830d8e0b2a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e39d12db9a838b54bcfeced4ea850af5a3770045f49ae7c40858d3dfc871780(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068c78edd334e54aa0cf2713ae876509a4a8c53a5c100562294ad4207ebaa857(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoColumnMaskUsing]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc30361cf56e8e683f0a3a9799b5474d3c10500c0993ddce381b6880e4489fc(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    for_securable_type: builtins.str,
    policy_type: builtins.str,
    to_principals: typing.Sequence[builtins.str],
    column_mask: typing.Optional[typing.Union[PolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
    match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    on_securable_fullname: typing.Optional[builtins.str] = None,
    on_securable_type: typing.Optional[builtins.str] = None,
    row_filter: typing.Optional[typing.Union[PolicyInfoRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    when_condition: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__514a6b6e9cbf8e83f0c3c11b91d076ca3108d9f4cd98759033a8d417dbc22f97(
    *,
    alias: typing.Optional[builtins.str] = None,
    condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69da653970c2772be9f2f583fb93d6a8856f1c390cd6c89d5176d12da97f0b0c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b284a9361b9b0d1733d6714c5906b3721809b06acf979657c4bd52bea6eae6d1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c90993ce56c1031a58e4b985aec049c34595f14dae95188e74261a166bcb999(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__242e1283e2efc0b0ae13b185652d7829ab54b295e6d58c33d8d479c296bf2b00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4cc9547685875d4cf0a761189a21f106b774e3fcf64b36abbcb9e593e94c3d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c40ce891d208ebac88a1b34ef2717eb608efb854a438fca125f3f8051da4d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoMatchColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15743eb0153c7567f602f8a986085fba96284f99131f0e76df89ca33cdfa57a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b4e476754d91e3a24e33b2d3077730714214b229e1869f23a7aa309d36d455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__896f70a68c2a7a489d66f61441f30f957fd5156b6e46bc7c94235dd4b6b33cbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b49ec4aa54706386ce4080464b967cf88015e561d74c8eb120e1785a1a9a57e2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoMatchColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3187e37c839cb793d697e845df5f1b1900c082af2fa507e3a68b339c669c6589(
    *,
    function_name: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c98b9fb6ecb41c47c16ade3e2b8bb25a65ca415d3ccba137bf165dec36e62a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511baecd919f32940a07dfcc424cffae0eade513c969910470d8bc6dccefc5b9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PolicyInfoRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0be7f86698198c78e1e8da7ad07e6c96fbeb40c47236d2b95580fe8f47555b4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd86e58643817a5efd76b4ff497b92c95c6cb54200e6c10b7aa6f80252808c56(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff6a70017a9ceee9bac5420a09ae0bb7069fc13475ef8bb073c39b9b1480a23(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb55e7a7239f72e7a86a44af211af47dee99188758422d2cc78531d7eb10bbb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bb1cf468994580f2ffb54d9c838103fc494b86a25474862fcac37a76ca6390a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1a47879dbf65f192636f0d7193824b884467f7d3320474d2b5528e6df660ef7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10536737c879006fd9dbc345be56620a1894460217e66559e86dc6e352e51bd0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00cac1eb3a26c630dbe514daec952cd21fbd7f32c23354ec9f53c8a12e50298b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__537924a1352df9fb7485ab3e9904e6b05c59d2d504a7a20b147d76e9c3a9d716(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PolicyInfoRowFilterUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c7a6c7d1652de360c7bfaa287060a179ed790deb3ddfba3b02b8dc945a0d57(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d412a184b0914b0fe8f7713ddbd2a6f369989558273329ccc58a0d1557b434(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f458b7ee60c49d0901d74cea7bd3c63b62a159dd7cb1476b51a5075678064a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b5e2c0458b3afcd701b08c9bcc330f86267bffb4678abc00b340900b5a9a398(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PolicyInfoRowFilterUsing]],
) -> None:
    """Type checking stubs"""
    pass
