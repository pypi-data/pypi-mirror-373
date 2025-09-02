r'''
# `data_databricks_policy_info`

Refer to the Terraform Registry for docs: [`data_databricks_policy_info`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info).
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


class DataDatabricksPolicyInfo(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfo",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info databricks_policy_info}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        for_securable_type: builtins.str,
        policy_type: builtins.str,
        to_principals: typing.Sequence[builtins.str],
        column_mask: typing.Optional[typing.Union["DataDatabricksPolicyInfoColumnMask", typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
        match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        on_securable_fullname: typing.Optional[builtins.str] = None,
        on_securable_type: typing.Optional[builtins.str] = None,
        row_filter: typing.Optional[typing.Union["DataDatabricksPolicyInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info databricks_policy_info} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param for_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#for_securable_type DataDatabricksPolicyInfo#for_securable_type}.
        :param policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#policy_type DataDatabricksPolicyInfo#policy_type}.
        :param to_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#to_principals DataDatabricksPolicyInfo#to_principals}.
        :param column_mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#column_mask DataDatabricksPolicyInfo#column_mask}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#comment DataDatabricksPolicyInfo#comment}.
        :param except_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#except_principals DataDatabricksPolicyInfo#except_principals}.
        :param match_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#match_columns DataDatabricksPolicyInfo#match_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#name DataDatabricksPolicyInfo#name}.
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_fullname DataDatabricksPolicyInfo#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_type DataDatabricksPolicyInfo#on_securable_type}.
        :param row_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#row_filter DataDatabricksPolicyInfo#row_filter}.
        :param when_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#when_condition DataDatabricksPolicyInfo#when_condition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#workspace_id DataDatabricksPolicyInfo#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12be3d6c2c78ea637146ddfdfccfc581f3f47b8843be43f10f7622db559446d9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksPolicyInfoConfig(
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
        '''Generates CDKTF code for importing a DataDatabricksPolicyInfo resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksPolicyInfo to import.
        :param import_from_id: The id of the existing DataDatabricksPolicyInfo that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksPolicyInfo to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74408d24e9ef2324999a2a582c2ed17aeac49746e9eb520c3a57cdcb990d8692)
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
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_column DataDatabricksPolicyInfo#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.
        '''
        value = DataDatabricksPolicyInfoColumnMask(
            function_name=function_name, on_column=on_column, using=using
        )

        return typing.cast(None, jsii.invoke(self, "putColumnMask", [value]))

    @jsii.member(jsii_name="putMatchColumns")
    def put_match_columns(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae3ad7f7b766fd4822719739a1affbbd99a70260b7a02dd27ca87a75e2bd39c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatchColumns", [value]))

    @jsii.member(jsii_name="putRowFilter")
    def put_row_filter(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.
        '''
        value = DataDatabricksPolicyInfoRowFilter(
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
    def column_mask(self) -> "DataDatabricksPolicyInfoColumnMaskOutputReference":
        return typing.cast("DataDatabricksPolicyInfoColumnMaskOutputReference", jsii.get(self, "columnMask"))

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
    def match_columns(self) -> "DataDatabricksPolicyInfoMatchColumnsList":
        return typing.cast("DataDatabricksPolicyInfoMatchColumnsList", jsii.get(self, "matchColumns"))

    @builtins.property
    @jsii.member(jsii_name="rowFilter")
    def row_filter(self) -> "DataDatabricksPolicyInfoRowFilterOutputReference":
        return typing.cast("DataDatabricksPolicyInfoRowFilterOutputReference", jsii.get(self, "rowFilter"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfoColumnMask"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfoColumnMask"]], jsii.get(self, "columnMaskInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoMatchColumns"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoMatchColumns"]]], jsii.get(self, "matchColumnsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfoRowFilter"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksPolicyInfoRowFilter"]], jsii.get(self, "rowFilterInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__8193eebd7a3dc052289f679ea0a23ee9fd1a6b6aafaede3c955eadc69583d05a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exceptPrincipals")
    def except_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exceptPrincipals"))

    @except_principals.setter
    def except_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91b4230c0533e0c64572dbbe65f8dc396af7fbaa77022b947690683e11afae9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exceptPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forSecurableType")
    def for_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forSecurableType"))

    @for_securable_type.setter
    def for_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c681c93236257e8f0903f701147e6ece06b7b97a5add18c57a1d2db65fcf6e8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd9eef278adda02b13d8384a59d985998c21532f9fffcd1d32dd54a77aae4f8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableFullname")
    def on_securable_fullname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableFullname"))

    @on_securable_fullname.setter
    def on_securable_fullname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d156ea7dd7cd9cff9a489e6348ceae500c83d516123b7b966658542c849a3d3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableFullname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSecurableType")
    def on_securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSecurableType"))

    @on_securable_type.setter
    def on_securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f05f31509dd1f319663304ada8b45c4d0e2b7101992f60f83e505b5f4a9419e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSecurableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyType"))

    @policy_type.setter
    def policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4969c388459f481d2b87d57efb63f656778ac7aa5a15e33a185dadfbfec4980d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toPrincipals")
    def to_principals(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "toPrincipals"))

    @to_principals.setter
    def to_principals(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d614c60b3a04945aac41d1625690321dfdd95e2de18cf409f26e384a1d2a6a72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whenCondition")
    def when_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "whenCondition"))

    @when_condition.setter
    def when_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b5008c7c49e444f3a9f103575d8e8eafe8867e6d9f699198fb49877e45f9010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whenCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef50fe739a1d93f2d50cbfe601fbf8f23046b89f7f6194db52aaaffd6c393c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoColumnMask",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "on_column": "onColumn",
        "using": "using",
    },
)
class DataDatabricksPolicyInfoColumnMask:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        on_column: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.
        :param on_column: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_column DataDatabricksPolicyInfo#on_column}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9e9b83d6ef35197e757fec6d7f875921bd767e3522900fdad1ca5ea69a9c07b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_column(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_column DataDatabricksPolicyInfo#on_column}.'''
        result = self._values.get("on_column")
        assert result is not None, "Required property 'on_column' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoColumnMaskUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoColumnMaskUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoColumnMask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfoColumnMaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoColumnMaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d76aa965715886953240984677fe670eacf38ee8f1669072b0bb68631a498e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoColumnMaskUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511c461d2e6c50721abeb6d3d868d4be5d101b4ef282fb79334b8b8d29802946)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "DataDatabricksPolicyInfoColumnMaskUsingList":
        return typing.cast("DataDatabricksPolicyInfoColumnMaskUsingList", jsii.get(self, "using"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoColumnMaskUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoColumnMaskUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dfb5a323c41c212f245f0d39c297085ec7b0bea1157e8fefca6b0ac5357b9b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onColumn")
    def on_column(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onColumn"))

    @on_column.setter
    def on_column(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14b3c47e99679aee1f450eb4792f776573a46e00a77ab8d323096847ae5a6c8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onColumn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adec8b4f6a64374d9c7df758f493d43b602580fb495a3e91bd42e72e6651654d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoColumnMaskUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class DataDatabricksPolicyInfoColumnMaskUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#constant DataDatabricksPolicyInfo#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1f3fd1f34541b0a3bb6badb92f8b29d317838b1e9e57adbeb7e7a994c0c12d7)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#constant DataDatabricksPolicyInfo#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoColumnMaskUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfoColumnMaskUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoColumnMaskUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c35b48d3615212d00728d5ddf28a09d20d5c399cbee6df6457373ace7d998ca3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfoColumnMaskUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7bfc85b5218796b76f545940dae591888af650e62f25f0f710b7f9e6338fdc9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfoColumnMaskUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__791d57ca24fe8e9ad72994e6c4f0a666609227791662f22af359395b34e23569)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65b34762ce2a2d68b6246f08a1079c132a1092a3e3c8706452799717be6343f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8db21c4d754083f80e8194b68c2960fee504ea114ed6614a77e50f7e8a0db28a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoColumnMaskUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoColumnMaskUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoColumnMaskUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__417127eca2cc293e56b4de0be5fcfc6898e7c2d3cbbd2419f1018c8e6f92f72f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfoColumnMaskUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoColumnMaskUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15c1642936b706d22e50c27fb0d25e14d740d815fe02e22d7f6dd0a2009a94d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b220307451593be1434c0788b0512087e4c14394d7e6fd815b23c83a93fc80a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba9365aaa26c4f3e11014867cb994561e46fdc22e05d5bf5a05c5d0c64c357db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMaskUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMaskUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMaskUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c64b3dcde3f93d5e2a5982831b159b8f687e02d5cfc392d7c1e50c71f69c8999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoConfig",
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
class DataDatabricksPolicyInfoConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        column_mask: typing.Optional[typing.Union[DataDatabricksPolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
        match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoMatchColumns", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        on_securable_fullname: typing.Optional[builtins.str] = None,
        on_securable_type: typing.Optional[builtins.str] = None,
        row_filter: typing.Optional[typing.Union["DataDatabricksPolicyInfoRowFilter", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param for_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#for_securable_type DataDatabricksPolicyInfo#for_securable_type}.
        :param policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#policy_type DataDatabricksPolicyInfo#policy_type}.
        :param to_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#to_principals DataDatabricksPolicyInfo#to_principals}.
        :param column_mask: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#column_mask DataDatabricksPolicyInfo#column_mask}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#comment DataDatabricksPolicyInfo#comment}.
        :param except_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#except_principals DataDatabricksPolicyInfo#except_principals}.
        :param match_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#match_columns DataDatabricksPolicyInfo#match_columns}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#name DataDatabricksPolicyInfo#name}.
        :param on_securable_fullname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_fullname DataDatabricksPolicyInfo#on_securable_fullname}.
        :param on_securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_type DataDatabricksPolicyInfo#on_securable_type}.
        :param row_filter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#row_filter DataDatabricksPolicyInfo#row_filter}.
        :param when_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#when_condition DataDatabricksPolicyInfo#when_condition}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#workspace_id DataDatabricksPolicyInfo#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(column_mask, dict):
            column_mask = DataDatabricksPolicyInfoColumnMask(**column_mask)
        if isinstance(row_filter, dict):
            row_filter = DataDatabricksPolicyInfoRowFilter(**row_filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d42bf01081d397a762a2d1456f146df8d3e18cf293262ffdce12f438f1c9a9eb)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#for_securable_type DataDatabricksPolicyInfo#for_securable_type}.'''
        result = self._values.get("for_securable_type")
        assert result is not None, "Required property 'for_securable_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#policy_type DataDatabricksPolicyInfo#policy_type}.'''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to_principals(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#to_principals DataDatabricksPolicyInfo#to_principals}.'''
        result = self._values.get("to_principals")
        assert result is not None, "Required property 'to_principals' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def column_mask(self) -> typing.Optional[DataDatabricksPolicyInfoColumnMask]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#column_mask DataDatabricksPolicyInfo#column_mask}.'''
        result = self._values.get("column_mask")
        return typing.cast(typing.Optional[DataDatabricksPolicyInfoColumnMask], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#comment DataDatabricksPolicyInfo#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def except_principals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#except_principals DataDatabricksPolicyInfo#except_principals}.'''
        result = self._values.get("except_principals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def match_columns(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoMatchColumns"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#match_columns DataDatabricksPolicyInfo#match_columns}.'''
        result = self._values.get("match_columns")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoMatchColumns"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#name DataDatabricksPolicyInfo#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_fullname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_fullname DataDatabricksPolicyInfo#on_securable_fullname}.'''
        result = self._values.get("on_securable_fullname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_securable_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#on_securable_type DataDatabricksPolicyInfo#on_securable_type}.'''
        result = self._values.get("on_securable_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def row_filter(self) -> typing.Optional["DataDatabricksPolicyInfoRowFilter"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#row_filter DataDatabricksPolicyInfo#row_filter}.'''
        result = self._values.get("row_filter")
        return typing.cast(typing.Optional["DataDatabricksPolicyInfoRowFilter"], result)

    @builtins.property
    def when_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#when_condition DataDatabricksPolicyInfo#when_condition}.'''
        result = self._values.get("when_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#workspace_id DataDatabricksPolicyInfo#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoMatchColumns",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "condition": "condition"},
)
class DataDatabricksPolicyInfoMatchColumns:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.
        :param condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#condition DataDatabricksPolicyInfo#condition}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ffb02b2723944ed9bf0630c8230a6262c744c8a0b8dfb8f6e6084f9130e26c5)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#condition DataDatabricksPolicyInfo#condition}.'''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoMatchColumns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfoMatchColumnsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoMatchColumnsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9211268f901ce660bfc981d63b0c5eb0f6ac61136bde9576364eb06cb41599ec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfoMatchColumnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdeb9bf47242263cf8e020db218c05289080c05157823e98224b7bde1f279591)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfoMatchColumnsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52e61775c1ca62a2b25ef0be932090fc3d942bed1949287f4d826b0fa3b653c0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e8495d78bfbaa57ae3a7bd7e5a114a13c7d1e11d0304c92c2c8bcfbdc901b08)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c08f4cb1b55a21714cece9316f91e09348cb1b71dc405645c3039c603cca2a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoMatchColumns]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoMatchColumns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoMatchColumns]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d55b8369fa804506de3e76d04f5731286a02b0cdd458136ef4d38f7b7fe47b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfoMatchColumnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoMatchColumnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__976e10658e820ec74c6fa60c4dcc8f4d80f2f338972082a0addfec9437b6a233)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b43ac552d4048063cf14f8150bc129d09d18c75d1541e04f3fe3c4206d24920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d1ea5ba0b24ca83fb0a37eaad5f909de12026897dd0b6df0de5253879494606)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoMatchColumns]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoMatchColumns]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoMatchColumns]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6339219be0d87e0abd793683d0aba2c3ba560f4ee1772a623e99e6902aa9a2da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoRowFilter",
    jsii_struct_bases=[],
    name_mapping={"function_name": "functionName", "using": "using"},
)
class DataDatabricksPolicyInfoRowFilter:
    def __init__(
        self,
        *,
        function_name: builtins.str,
        using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param function_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.
        :param using: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6111d188b8dc2ea549570d1a43a4c751b057794b363d510be2053acee0c3c9c9)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument using", value=using, expected_type=type_hints["using"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "function_name": function_name,
        }
        if using is not None:
            self._values["using"] = using

    @builtins.property
    def function_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#function_name DataDatabricksPolicyInfo#function_name}.'''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def using(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoRowFilterUsing"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#using DataDatabricksPolicyInfo#using}.'''
        result = self._values.get("using")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoRowFilterUsing"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoRowFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfoRowFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoRowFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af285b63b7d86a40ab3a9b319f04d7ccb31e78abc4806a034baecdfc7b645b30)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUsing")
    def put_using(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksPolicyInfoRowFilterUsing", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dd0b3626e5232f8e1c2097bff5af5534f9fbcc015969b4a9ef865d615eaa961)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUsing", [value]))

    @jsii.member(jsii_name="resetUsing")
    def reset_using(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsing", []))

    @builtins.property
    @jsii.member(jsii_name="using")
    def using(self) -> "DataDatabricksPolicyInfoRowFilterUsingList":
        return typing.cast("DataDatabricksPolicyInfoRowFilterUsingList", jsii.get(self, "using"))

    @builtins.property
    @jsii.member(jsii_name="functionNameInput")
    def function_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="usingInput")
    def using_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoRowFilterUsing"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksPolicyInfoRowFilterUsing"]]], jsii.get(self, "usingInput"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd45eda8eb81dd5e7b300ce6dea869853bdc59f0ab174539f98f8f5cf3d202be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c174f5dc0998c63233f51ddec7c04925e83ffa806c241558526f8b4ce99fbad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoRowFilterUsing",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias", "constant": "constant"},
)
class DataDatabricksPolicyInfoRowFilterUsing:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        constant: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.
        :param constant: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#constant DataDatabricksPolicyInfo#constant}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b1cbafd23f5a6d6c2dca05a3d42d93990da02e6459b24d2b6d900932488d6b0)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument constant", value=constant, expected_type=type_hints["constant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if constant is not None:
            self._values["constant"] = constant

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#alias DataDatabricksPolicyInfo#alias}.'''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constant(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/policy_info#constant DataDatabricksPolicyInfo#constant}.'''
        result = self._values.get("constant")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksPolicyInfoRowFilterUsing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksPolicyInfoRowFilterUsingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoRowFilterUsingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8bbe8fd336fa0146584b049cb070f07e920ee2fb779f06c480138396f83293d7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksPolicyInfoRowFilterUsingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70d8ffb1bf2f844e605a311602ce0bfd1f673292f8a3dfe152df3b46f4871a98)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksPolicyInfoRowFilterUsingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c62feda1d5ff0f2f54cbba66746de74fb8a09a90beaa71d10e17ea5ca0dd30e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__80b78db47fa9f557f48ff7b78f81fb8e7ccea9327082191e5f3560c18f0df274)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7f9caa63e66825c97bf8602b016be10f19bf696d90a1f837d9d2b667216dee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoRowFilterUsing]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoRowFilterUsing]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoRowFilterUsing]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a245a5040d7b78ceb0224dd1a572a6bcd44ba32f8937aa0a50ee4f93ead79c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksPolicyInfoRowFilterUsingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksPolicyInfo.DataDatabricksPolicyInfoRowFilterUsingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de2e1df1a7da0797e58f6af0c4f79045d1dcc074c8ba3b01360b0f54af0d9c1b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92d282d97f2e918c1116e1d1b4ee745a0f10d5f0af579c6940cc96ee9433fefe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="constant")
    def constant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "constant"))

    @constant.setter
    def constant(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2058d8d08c3bd6f5ebcf2ca46a1ccc225fa004954adb5b5a951dc847542bacc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "constant", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilterUsing]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilterUsing]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilterUsing]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b8fbd6eb3e660f997bb78b6b66d5fbdb1e9c5a04937360b255f4b54653f8f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksPolicyInfo",
    "DataDatabricksPolicyInfoColumnMask",
    "DataDatabricksPolicyInfoColumnMaskOutputReference",
    "DataDatabricksPolicyInfoColumnMaskUsing",
    "DataDatabricksPolicyInfoColumnMaskUsingList",
    "DataDatabricksPolicyInfoColumnMaskUsingOutputReference",
    "DataDatabricksPolicyInfoConfig",
    "DataDatabricksPolicyInfoMatchColumns",
    "DataDatabricksPolicyInfoMatchColumnsList",
    "DataDatabricksPolicyInfoMatchColumnsOutputReference",
    "DataDatabricksPolicyInfoRowFilter",
    "DataDatabricksPolicyInfoRowFilterOutputReference",
    "DataDatabricksPolicyInfoRowFilterUsing",
    "DataDatabricksPolicyInfoRowFilterUsingList",
    "DataDatabricksPolicyInfoRowFilterUsingOutputReference",
]

publication.publish()

def _typecheckingstub__12be3d6c2c78ea637146ddfdfccfc581f3f47b8843be43f10f7622db559446d9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    for_securable_type: builtins.str,
    policy_type: builtins.str,
    to_principals: typing.Sequence[builtins.str],
    column_mask: typing.Optional[typing.Union[DataDatabricksPolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
    match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    on_securable_fullname: typing.Optional[builtins.str] = None,
    on_securable_type: typing.Optional[builtins.str] = None,
    row_filter: typing.Optional[typing.Union[DataDatabricksPolicyInfoRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__74408d24e9ef2324999a2a582c2ed17aeac49746e9eb520c3a57cdcb990d8692(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3ad7f7b766fd4822719739a1affbbd99a70260b7a02dd27ca87a75e2bd39c6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8193eebd7a3dc052289f679ea0a23ee9fd1a6b6aafaede3c955eadc69583d05a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91b4230c0533e0c64572dbbe65f8dc396af7fbaa77022b947690683e11afae9a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c681c93236257e8f0903f701147e6ece06b7b97a5add18c57a1d2db65fcf6e8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd9eef278adda02b13d8384a59d985998c21532f9fffcd1d32dd54a77aae4f8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d156ea7dd7cd9cff9a489e6348ceae500c83d516123b7b966658542c849a3d3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f05f31509dd1f319663304ada8b45c4d0e2b7101992f60f83e505b5f4a9419e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4969c388459f481d2b87d57efb63f656778ac7aa5a15e33a185dadfbfec4980d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d614c60b3a04945aac41d1625690321dfdd95e2de18cf409f26e384a1d2a6a72(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5008c7c49e444f3a9f103575d8e8eafe8867e6d9f699198fb49877e45f9010(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef50fe739a1d93f2d50cbfe601fbf8f23046b89f7f6194db52aaaffd6c393c9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9e9b83d6ef35197e757fec6d7f875921bd767e3522900fdad1ca5ea69a9c07b(
    *,
    function_name: builtins.str,
    on_column: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d76aa965715886953240984677fe670eacf38ee8f1669072b0bb68631a498e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511c461d2e6c50721abeb6d3d868d4be5d101b4ef282fb79334b8b8d29802946(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoColumnMaskUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dfb5a323c41c212f245f0d39c297085ec7b0bea1157e8fefca6b0ac5357b9b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14b3c47e99679aee1f450eb4792f776573a46e00a77ab8d323096847ae5a6c8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adec8b4f6a64374d9c7df758f493d43b602580fb495a3e91bd42e72e6651654d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1f3fd1f34541b0a3bb6badb92f8b29d317838b1e9e57adbeb7e7a994c0c12d7(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35b48d3615212d00728d5ddf28a09d20d5c399cbee6df6457373ace7d998ca3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7bfc85b5218796b76f545940dae591888af650e62f25f0f710b7f9e6338fdc9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__791d57ca24fe8e9ad72994e6c4f0a666609227791662f22af359395b34e23569(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b34762ce2a2d68b6246f08a1079c132a1092a3e3c8706452799717be6343f2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8db21c4d754083f80e8194b68c2960fee504ea114ed6614a77e50f7e8a0db28a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__417127eca2cc293e56b4de0be5fcfc6898e7c2d3cbbd2419f1018c8e6f92f72f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoColumnMaskUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15c1642936b706d22e50c27fb0d25e14d740d815fe02e22d7f6dd0a2009a94d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b220307451593be1434c0788b0512087e4c14394d7e6fd815b23c83a93fc80a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba9365aaa26c4f3e11014867cb994561e46fdc22e05d5bf5a05c5d0c64c357db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c64b3dcde3f93d5e2a5982831b159b8f687e02d5cfc392d7c1e50c71f69c8999(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoColumnMaskUsing]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d42bf01081d397a762a2d1456f146df8d3e18cf293262ffdce12f438f1c9a9eb(
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
    column_mask: typing.Optional[typing.Union[DataDatabricksPolicyInfoColumnMask, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    except_principals: typing.Optional[typing.Sequence[builtins.str]] = None,
    match_columns: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoMatchColumns, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    on_securable_fullname: typing.Optional[builtins.str] = None,
    on_securable_type: typing.Optional[builtins.str] = None,
    row_filter: typing.Optional[typing.Union[DataDatabricksPolicyInfoRowFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    when_condition: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ffb02b2723944ed9bf0630c8230a6262c744c8a0b8dfb8f6e6084f9130e26c5(
    *,
    alias: typing.Optional[builtins.str] = None,
    condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9211268f901ce660bfc981d63b0c5eb0f6ac61136bde9576364eb06cb41599ec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdeb9bf47242263cf8e020db218c05289080c05157823e98224b7bde1f279591(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e61775c1ca62a2b25ef0be932090fc3d942bed1949287f4d826b0fa3b653c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e8495d78bfbaa57ae3a7bd7e5a114a13c7d1e11d0304c92c2c8bcfbdc901b08(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c08f4cb1b55a21714cece9316f91e09348cb1b71dc405645c3039c603cca2a8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d55b8369fa804506de3e76d04f5731286a02b0cdd458136ef4d38f7b7fe47b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoMatchColumns]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976e10658e820ec74c6fa60c4dcc8f4d80f2f338972082a0addfec9437b6a233(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b43ac552d4048063cf14f8150bc129d09d18c75d1541e04f3fe3c4206d24920(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d1ea5ba0b24ca83fb0a37eaad5f909de12026897dd0b6df0de5253879494606(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6339219be0d87e0abd793683d0aba2c3ba560f4ee1772a623e99e6902aa9a2da(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoMatchColumns]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6111d188b8dc2ea549570d1a43a4c751b057794b363d510be2053acee0c3c9c9(
    *,
    function_name: builtins.str,
    using: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af285b63b7d86a40ab3a9b319f04d7ccb31e78abc4806a034baecdfc7b645b30(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dd0b3626e5232f8e1c2097bff5af5534f9fbcc015969b4a9ef865d615eaa961(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksPolicyInfoRowFilterUsing, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd45eda8eb81dd5e7b300ce6dea869853bdc59f0ab174539f98f8f5cf3d202be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c174f5dc0998c63233f51ddec7c04925e83ffa806c241558526f8b4ce99fbad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b1cbafd23f5a6d6c2dca05a3d42d93990da02e6459b24d2b6d900932488d6b0(
    *,
    alias: typing.Optional[builtins.str] = None,
    constant: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bbe8fd336fa0146584b049cb070f07e920ee2fb779f06c480138396f83293d7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d8ffb1bf2f844e605a311602ce0bfd1f673292f8a3dfe152df3b46f4871a98(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c62feda1d5ff0f2f54cbba66746de74fb8a09a90beaa71d10e17ea5ca0dd30e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b78db47fa9f557f48ff7b78f81fb8e7ccea9327082191e5f3560c18f0df274(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7f9caa63e66825c97bf8602b016be10f19bf696d90a1f837d9d2b667216dee2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a245a5040d7b78ceb0224dd1a572a6bcd44ba32f8937aa0a50ee4f93ead79c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksPolicyInfoRowFilterUsing]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de2e1df1a7da0797e58f6af0c4f79045d1dcc074c8ba3b01360b0f54af0d9c1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d282d97f2e918c1116e1d1b4ee745a0f10d5f0af579c6940cc96ee9433fefe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2058d8d08c3bd6f5ebcf2ca46a1ccc225fa004954adb5b5a951dc847542bacc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b8fbd6eb3e660f997bb78b6b66d5fbdb1e9c5a04937360b255f4b54653f8f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksPolicyInfoRowFilterUsing]],
) -> None:
    """Type checking stubs"""
    pass
