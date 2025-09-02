r'''
# `databricks_account_setting_v2`

Refer to the Terraform Registry for docs: [`databricks_account_setting_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2).
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


class AccountSettingV2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2 databricks_account_setting_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["AccountSettingV2AibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["AccountSettingV2AibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union["AccountSettingV2BooleanVal", typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["AccountSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["AccountSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["AccountSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["AccountSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["AccountSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["AccountSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["AccountSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["AccountSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2 databricks_account_setting_v2} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_access_policy AccountSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_approved_domains AccountSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#automatic_cluster_update_workspace AccountSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#boolean_val AccountSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#default_data_security_mode AccountSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy AccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains AccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_automatic_cluster_update_workspace AccountSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_default_data_security_mode AccountSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_personal_compute AccountSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_restrict_workspace_admins AccountSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#integer_val AccountSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#name AccountSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#personal_compute AccountSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restrict_workspace_admins AccountSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#string_val AccountSettingV2#string_val}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05440c638d02a166d37692133a522e493cd3fa6f257e124ad65b1b7a8b6edf65)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AccountSettingV2Config(
            aibi_dashboard_embedding_access_policy=aibi_dashboard_embedding_access_policy,
            aibi_dashboard_embedding_approved_domains=aibi_dashboard_embedding_approved_domains,
            automatic_cluster_update_workspace=automatic_cluster_update_workspace,
            boolean_val=boolean_val,
            default_data_security_mode=default_data_security_mode,
            effective_aibi_dashboard_embedding_access_policy=effective_aibi_dashboard_embedding_access_policy,
            effective_aibi_dashboard_embedding_approved_domains=effective_aibi_dashboard_embedding_approved_domains,
            effective_automatic_cluster_update_workspace=effective_automatic_cluster_update_workspace,
            effective_default_data_security_mode=effective_default_data_security_mode,
            effective_personal_compute=effective_personal_compute,
            effective_restrict_workspace_admins=effective_restrict_workspace_admins,
            integer_val=integer_val,
            name=name,
            personal_compute=personal_compute,
            restrict_workspace_admins=restrict_workspace_admins,
            string_val=string_val,
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
        '''Generates CDKTF code for importing a AccountSettingV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AccountSettingV2 to import.
        :param import_from_id: The id of the existing AccountSettingV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AccountSettingV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8d3b5edd4077e29d08f40f6f387cc0fdafcf7e79365b96281976564e9a64dc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAibiDashboardEmbeddingAccessPolicy")
    def put_aibi_dashboard_embedding_access_policy(
        self,
        *,
        access_policy_type: builtins.str,
    ) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.
        '''
        value = AccountSettingV2AibiDashboardEmbeddingAccessPolicy(
            access_policy_type=access_policy_type
        )

        return typing.cast(None, jsii.invoke(self, "putAibiDashboardEmbeddingAccessPolicy", [value]))

    @jsii.member(jsii_name="putAibiDashboardEmbeddingApprovedDomains")
    def put_aibi_dashboard_embedding_approved_domains(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.
        '''
        value = AccountSettingV2AibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putAutomaticClusterUpdateWorkspace")
    def put_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.
        '''
        value = AccountSettingV2AutomaticClusterUpdateWorkspace(
            can_toggle=can_toggle,
            enabled=enabled,
            enablement_details=enablement_details,
            maintenance_window=maintenance_window,
            restart_even_if_no_updates_available=restart_even_if_no_updates_available,
        )

        return typing.cast(None, jsii.invoke(self, "putAutomaticClusterUpdateWorkspace", [value]))

    @jsii.member(jsii_name="putBooleanVal")
    def put_boolean_val(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        value_ = AccountSettingV2BooleanVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putBooleanVal", [value_]))

    @jsii.member(jsii_name="putDefaultDataSecurityMode")
    def put_default_data_security_mode(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        value = AccountSettingV2DefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectiveAibiDashboardEmbeddingAccessPolicy")
    def put_effective_aibi_dashboard_embedding_access_policy(
        self,
        *,
        access_policy_type: builtins.str,
    ) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.
        '''
        value = AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(
            access_policy_type=access_policy_type
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAibiDashboardEmbeddingAccessPolicy", [value]))

    @jsii.member(jsii_name="putEffectiveAibiDashboardEmbeddingApprovedDomains")
    def put_effective_aibi_dashboard_embedding_approved_domains(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.
        '''
        value = AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putEffectiveAutomaticClusterUpdateWorkspace")
    def put_effective_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.
        '''
        value = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(
            can_toggle=can_toggle,
            enabled=enabled,
            enablement_details=enablement_details,
            maintenance_window=maintenance_window,
            restart_even_if_no_updates_available=restart_even_if_no_updates_available,
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAutomaticClusterUpdateWorkspace", [value]))

    @jsii.member(jsii_name="putEffectiveDefaultDataSecurityMode")
    def put_effective_default_data_security_mode(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        value = AccountSettingV2EffectiveDefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putEffectiveDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectivePersonalCompute")
    def put_effective_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        value_ = AccountSettingV2EffectivePersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putEffectivePersonalCompute", [value_]))

    @jsii.member(jsii_name="putEffectiveRestrictWorkspaceAdmins")
    def put_effective_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        value = AccountSettingV2EffectiveRestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putEffectiveRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putIntegerVal")
    def put_integer_val(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        value_ = AccountSettingV2IntegerVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putIntegerVal", [value_]))

    @jsii.member(jsii_name="putPersonalCompute")
    def put_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        value_ = AccountSettingV2PersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putPersonalCompute", [value_]))

    @jsii.member(jsii_name="putRestrictWorkspaceAdmins")
    def put_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        value = AccountSettingV2RestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putStringVal")
    def put_string_val(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        value_ = AccountSettingV2StringVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putStringVal", [value_]))

    @jsii.member(jsii_name="resetAibiDashboardEmbeddingAccessPolicy")
    def reset_aibi_dashboard_embedding_access_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAibiDashboardEmbeddingAccessPolicy", []))

    @jsii.member(jsii_name="resetAibiDashboardEmbeddingApprovedDomains")
    def reset_aibi_dashboard_embedding_approved_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAibiDashboardEmbeddingApprovedDomains", []))

    @jsii.member(jsii_name="resetAutomaticClusterUpdateWorkspace")
    def reset_automatic_cluster_update_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticClusterUpdateWorkspace", []))

    @jsii.member(jsii_name="resetBooleanVal")
    def reset_boolean_val(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBooleanVal", []))

    @jsii.member(jsii_name="resetDefaultDataSecurityMode")
    def reset_default_data_security_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultDataSecurityMode", []))

    @jsii.member(jsii_name="resetEffectiveAibiDashboardEmbeddingAccessPolicy")
    def reset_effective_aibi_dashboard_embedding_access_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveAibiDashboardEmbeddingAccessPolicy", []))

    @jsii.member(jsii_name="resetEffectiveAibiDashboardEmbeddingApprovedDomains")
    def reset_effective_aibi_dashboard_embedding_approved_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveAibiDashboardEmbeddingApprovedDomains", []))

    @jsii.member(jsii_name="resetEffectiveAutomaticClusterUpdateWorkspace")
    def reset_effective_automatic_cluster_update_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveAutomaticClusterUpdateWorkspace", []))

    @jsii.member(jsii_name="resetEffectiveDefaultDataSecurityMode")
    def reset_effective_default_data_security_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveDefaultDataSecurityMode", []))

    @jsii.member(jsii_name="resetEffectivePersonalCompute")
    def reset_effective_personal_compute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectivePersonalCompute", []))

    @jsii.member(jsii_name="resetEffectiveRestrictWorkspaceAdmins")
    def reset_effective_restrict_workspace_admins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveRestrictWorkspaceAdmins", []))

    @jsii.member(jsii_name="resetIntegerVal")
    def reset_integer_val(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegerVal", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPersonalCompute")
    def reset_personal_compute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPersonalCompute", []))

    @jsii.member(jsii_name="resetRestrictWorkspaceAdmins")
    def reset_restrict_workspace_admins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictWorkspaceAdmins", []))

    @jsii.member(jsii_name="resetStringVal")
    def reset_string_val(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStringVal", []))

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
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicy")
    def aibi_dashboard_embedding_access_policy(
        self,
    ) -> "AccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("AccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "aibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomains")
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "AccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("AccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "aibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspace")
    def automatic_cluster_update_workspace(
        self,
    ) -> "AccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("AccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "automaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="booleanVal")
    def boolean_val(self) -> "AccountSettingV2BooleanValOutputReference":
        return typing.cast("AccountSettingV2BooleanValOutputReference", jsii.get(self, "booleanVal"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityMode")
    def default_data_security_mode(
        self,
    ) -> "AccountSettingV2DefaultDataSecurityModeOutputReference":
        return typing.cast("AccountSettingV2DefaultDataSecurityModeOutputReference", jsii.get(self, "defaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicy")
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomains")
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspace")
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "effectiveAutomaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="effectiveBooleanVal")
    def effective_boolean_val(
        self,
    ) -> "AccountSettingV2EffectiveBooleanValOutputReference":
        return typing.cast("AccountSettingV2EffectiveBooleanValOutputReference", jsii.get(self, "effectiveBooleanVal"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityMode")
    def effective_default_data_security_mode(
        self,
    ) -> "AccountSettingV2EffectiveDefaultDataSecurityModeOutputReference":
        return typing.cast("AccountSettingV2EffectiveDefaultDataSecurityModeOutputReference", jsii.get(self, "effectiveDefaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveIntegerVal")
    def effective_integer_val(
        self,
    ) -> "AccountSettingV2EffectiveIntegerValOutputReference":
        return typing.cast("AccountSettingV2EffectiveIntegerValOutputReference", jsii.get(self, "effectiveIntegerVal"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalCompute")
    def effective_personal_compute(
        self,
    ) -> "AccountSettingV2EffectivePersonalComputeOutputReference":
        return typing.cast("AccountSettingV2EffectivePersonalComputeOutputReference", jsii.get(self, "effectivePersonalCompute"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdmins")
    def effective_restrict_workspace_admins(
        self,
    ) -> "AccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference":
        return typing.cast("AccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference", jsii.get(self, "effectiveRestrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="effectiveStringVal")
    def effective_string_val(
        self,
    ) -> "AccountSettingV2EffectiveStringValOutputReference":
        return typing.cast("AccountSettingV2EffectiveStringValOutputReference", jsii.get(self, "effectiveStringVal"))

    @builtins.property
    @jsii.member(jsii_name="integerVal")
    def integer_val(self) -> "AccountSettingV2IntegerValOutputReference":
        return typing.cast("AccountSettingV2IntegerValOutputReference", jsii.get(self, "integerVal"))

    @builtins.property
    @jsii.member(jsii_name="personalCompute")
    def personal_compute(self) -> "AccountSettingV2PersonalComputeOutputReference":
        return typing.cast("AccountSettingV2PersonalComputeOutputReference", jsii.get(self, "personalCompute"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdmins")
    def restrict_workspace_admins(
        self,
    ) -> "AccountSettingV2RestrictWorkspaceAdminsOutputReference":
        return typing.cast("AccountSettingV2RestrictWorkspaceAdminsOutputReference", jsii.get(self, "restrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="stringVal")
    def string_val(self) -> "AccountSettingV2StringValOutputReference":
        return typing.cast("AccountSettingV2StringValOutputReference", jsii.get(self, "stringVal"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicyInput")
    def aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "aibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomainsInput")
    def aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "aibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspaceInput")
    def automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspace"]], jsii.get(self, "automaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="booleanValInput")
    def boolean_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2BooleanVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2BooleanVal"]], jsii.get(self, "booleanValInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityModeInput")
    def default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2DefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2DefaultDataSecurityMode"]], jsii.get(self, "defaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicyInput")
    def effective_aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomainsInput")
    def effective_aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspaceInput")
    def effective_automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]], jsii.get(self, "effectiveAutomaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityModeInput")
    def effective_default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveDefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveDefaultDataSecurityMode"]], jsii.get(self, "effectiveDefaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalComputeInput")
    def effective_personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectivePersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectivePersonalCompute"]], jsii.get(self, "effectivePersonalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdminsInput")
    def effective_restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveRestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveRestrictWorkspaceAdmins"]], jsii.get(self, "effectiveRestrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="integerValInput")
    def integer_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2IntegerVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2IntegerVal"]], jsii.get(self, "integerValInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="personalComputeInput")
    def personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2PersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2PersonalCompute"]], jsii.get(self, "personalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdminsInput")
    def restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2RestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2RestrictWorkspaceAdmins"]], jsii.get(self, "restrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="stringValInput")
    def string_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2StringVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2StringVal"]], jsii.get(self, "stringValInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79ccc01b884abb530e85ebbcd25c8b068b1d766514363f6ac019b08daea61b2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class AccountSettingV2AibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3140b4aee6c2d40283b7a42c4f3ba3f1958f97f730788b93bcf6d66e7e9cf5b3)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f61a1cdf785b3513cc978b8a0cfd54582033706eb5164c1512692fb45dfafd5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="accessPolicyTypeInput")
    def access_policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPolicyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="accessPolicyType")
    def access_policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPolicyType"))

    @access_policy_type.setter
    def access_policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__540dcfbb590b9e55dfe72cfb537c548d61fc4c49e896a92c5398f6d1768220b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51782d718040e5ca57e255bf4863bbd7501a9c505c57f907f3c80ee47e629bce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class AccountSettingV2AibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088616014d0dd80119e5f525574a5ab5980b13dd892eea385aec3d4983e25393)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50e4d0f887403a965f6dd573376976c6cf8a0113452004fef2159cf69108d0ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetApprovedDomains")
    def reset_approved_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApprovedDomains", []))

    @builtins.property
    @jsii.member(jsii_name="approvedDomainsInput")
    def approved_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "approvedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="approvedDomains")
    def approved_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "approvedDomains"))

    @approved_domains.setter
    def approved_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6395529b0a90617c37f11f558ca4fa3b9ecb7d47229ecd795ad7d89b762ce89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0098dcb7758a9f1772a633f3c61bfe9ddd740537c363bf4e0630685fa72eff72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class AccountSettingV2AutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12370d75cdcaaa38e41b65431ebb0159ec940c9f8ef673542eb5969f55b87def)
            check_type(argname="argument can_toggle", value=can_toggle, expected_type=type_hints["can_toggle"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument enablement_details", value=enablement_details, expected_type=type_hints["enablement_details"])
            check_type(argname="argument maintenance_window", value=maintenance_window, expected_type=type_hints["maintenance_window"])
            check_type(argname="argument restart_even_if_no_updates_available", value=restart_even_if_no_updates_available, expected_type=type_hints["restart_even_if_no_updates_available"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if can_toggle is not None:
            self._values["can_toggle"] = can_toggle
        if enabled is not None:
            self._values["enabled"] = enabled
        if enablement_details is not None:
            self._values["enablement_details"] = enablement_details
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if restart_even_if_no_updates_available is not None:
            self._values["restart_even_if_no_updates_available"] = restart_even_if_no_updates_available

    @builtins.property
    def can_toggle(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb524cad5b281cff1b9c7aab60aa8e0e501573cc0f6a6798a3fa16741816e79)
            check_type(argname="argument forced_for_compliance_mode", value=forced_for_compliance_mode, expected_type=type_hints["forced_for_compliance_mode"])
            check_type(argname="argument unavailable_for_disabled_entitlement", value=unavailable_for_disabled_entitlement, expected_type=type_hints["unavailable_for_disabled_entitlement"])
            check_type(argname="argument unavailable_for_non_enterprise_tier", value=unavailable_for_non_enterprise_tier, expected_type=type_hints["unavailable_for_non_enterprise_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if forced_for_compliance_mode is not None:
            self._values["forced_for_compliance_mode"] = forced_for_compliance_mode
        if unavailable_for_disabled_entitlement is not None:
            self._values["unavailable_for_disabled_entitlement"] = unavailable_for_disabled_entitlement
        if unavailable_for_non_enterprise_tier is not None:
            self._values["unavailable_for_non_enterprise_tier"] = unavailable_for_non_enterprise_tier

    @builtins.property
    def forced_for_compliance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__015da414e8f306d01f13612a7b546dc3a2982145449f94e2e42806aa550b1e8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetForcedForComplianceMode")
    def reset_forced_for_compliance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForcedForComplianceMode", []))

    @jsii.member(jsii_name="resetUnavailableForDisabledEntitlement")
    def reset_unavailable_for_disabled_entitlement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForDisabledEntitlement", []))

    @jsii.member(jsii_name="resetUnavailableForNonEnterpriseTier")
    def reset_unavailable_for_non_enterprise_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForNonEnterpriseTier", []))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceModeInput")
    def forced_for_compliance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forcedForComplianceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlementInput")
    def unavailable_for_disabled_entitlement_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForDisabledEntitlementInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTierInput")
    def unavailable_for_non_enterprise_tier_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForNonEnterpriseTierInput"))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceMode")
    def forced_for_compliance_mode(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forcedForComplianceMode"))

    @forced_for_compliance_mode.setter
    def forced_for_compliance_mode(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eea0e98008b365a0b4d59ac618fc9b535fe188b9979e5785559b265db2d1d4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forcedForComplianceMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlement")
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForDisabledEntitlement"))

    @unavailable_for_disabled_entitlement.setter
    def unavailable_for_disabled_entitlement(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8583d3c67fca45cb7085efe53ce08053e2daa690f4a90abbf530514a00a154)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForDisabledEntitlement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTier")
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForNonEnterpriseTier"))

    @unavailable_for_non_enterprise_tier.setter
    def unavailable_for_non_enterprise_tier(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7531c182aeab7309cd317d914ba839c84465fd2daeb3461209ee18c7eb4fbc21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c73c53049f192ef13d0008d5848db36ee38dc04d2179f959ce0e8a57df9edbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0638f7ad8f66d17347ba4f11f952f624a7e8e1a806988b76729980d1a5ef13a4)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__832fcf26b16ff0c89196897a899866fbaacae6c2931b7f6275cb8cea6f871ff2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.
        '''
        value = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
            day_of_week=day_of_week,
            frequency=frequency,
            window_start_time=window_start_time,
        )

        return typing.cast(None, jsii.invoke(self, "putWeekDayBasedSchedule", [value]))

    @jsii.member(jsii_name="resetWeekDayBasedSchedule")
    def reset_week_day_based_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeekDayBasedSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedSchedule")
    def week_day_based_schedule(
        self,
    ) -> "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa56845b772c4e30e650dd7ee768c8d5ebffa424ad7e708c329a4f8f3401f1c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b43491c365ee54d91fe9cc401fe4b7e3c1603ea8ca9acae4444137643e0ba77)
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument window_start_time", value=window_start_time, expected_type=type_hints["window_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day_of_week is not None:
            self._values["day_of_week"] = day_of_week
        if frequency is not None:
            self._values["frequency"] = frequency
        if window_start_time is not None:
            self._values["window_start_time"] = window_start_time

    @builtins.property
    def day_of_week(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f099a6eeebf327cf708367ae1c530f5884dba46ef5a1f14cf23b8e902ed3ce91)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWindowStartTime")
    def put_window_start_time(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.
        '''
        value = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
            hours=hours, minutes=minutes
        )

        return typing.cast(None, jsii.invoke(self, "putWindowStartTime", [value]))

    @jsii.member(jsii_name="resetDayOfWeek")
    def reset_day_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDayOfWeek", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetWindowStartTime")
    def reset_window_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowStartTime", []))

    @builtins.property
    @jsii.member(jsii_name="windowStartTime")
    def window_start_time(
        self,
    ) -> "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property
    @jsii.member(jsii_name="windowStartTimeInput")
    def window_start_time_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17cf2a848ae24e8ef9891cd99dd16a942691aa0ba8c9a294b147ed84cee34f4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__693da47f83d3accb0df97721818d3fa1099aab22ce89928959494ed25a2055b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a07928397134c32f678c719805c33e5c93f14e35958a61cb7b129676814a6a9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c04054b0bc67f163119c78311193a1130005ae83a386f68ad976c22a0d8459)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e56fa5f4432692a3f0f5a8fbbdfc7fedafdee07fcbaba51d57de9663a2b69586)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHours")
    def reset_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHours", []))

    @jsii.member(jsii_name="resetMinutes")
    def reset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinutes", []))

    @builtins.property
    @jsii.member(jsii_name="hoursInput")
    def hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hoursInput"))

    @builtins.property
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property
    @jsii.member(jsii_name="hours")
    def hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hours"))

    @hours.setter
    def hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d438d0e8cedbd80f4ae03a8163f4332b9722a334724a7455eea0e4402ec7edd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__235a49a1f7dfd61ae8a35b85581337fb1c54e0b571b9d8c52a303b89330d944b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9477b4fdbd39cefa8cb8caaec2196bb8b565e5efaf1bdaecf761e581e6cdcbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9c5e1aeda3dac627c8e5b3651443946372547d883d4223e649f13cab1e0cab2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEnablementDetails")
    def put_enablement_details(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.
        '''
        value = AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(
            week_day_based_schedule=week_day_based_schedule
        )

        return typing.cast(None, jsii.invoke(self, "putMaintenanceWindow", [value]))

    @jsii.member(jsii_name="resetCanToggle")
    def reset_can_toggle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanToggle", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnablementDetails")
    def reset_enablement_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablementDetails", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetRestartEvenIfNoUpdatesAvailable")
    def reset_restart_even_if_no_updates_available(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartEvenIfNoUpdatesAvailable", []))

    @builtins.property
    @jsii.member(jsii_name="enablementDetails")
    def enablement_details(
        self,
    ) -> AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

    @builtins.property
    @jsii.member(jsii_name="canToggleInput")
    def can_toggle_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "canToggleInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enablementDetailsInput")
    def enablement_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailableInput")
    def restart_even_if_no_updates_available_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "restartEvenIfNoUpdatesAvailableInput"))

    @builtins.property
    @jsii.member(jsii_name="canToggle")
    def can_toggle(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "canToggle"))

    @can_toggle.setter
    def can_toggle(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55c3cd6552d8994987aa6d1482757fb4b256d157ab29e59c12a65190aa8f9e42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canToggle", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__cf3ee418953deb220ce9eda992b0ce7593a6d3f162084416d1c29fd64e4b21ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailable")
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "restartEvenIfNoUpdatesAvailable"))

    @restart_even_if_no_updates_available.setter
    def restart_even_if_no_updates_available(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d83e54086f4fda010ea2370d9de00a2fd602a4a5f5c88b287c9b530509de3ce8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26699902ff95b76c35bb8e801c91582a31f7fbbc78115aa7c88355f2a9e7117d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2BooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2BooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb451bac3ed4cb8034da33a42ad301f2f886eb23ccf7b8fb6f060724221a109f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2BooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2BooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2BooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65e73a11a7b01146e28100c0d4b0c528aa5e10cd0ef4a1556b42f5340f8559fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "value"))

    @value.setter
    def value(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47f730cd1c39c62370a9b582466a24bd16269f261ad02cadd8736bb8fde4eaea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2BooleanVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2BooleanVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2BooleanVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e08b0fd3edb59e476dd2ec47f698da8717a8fb5723d440a88d1cc308b57909f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "aibi_dashboard_embedding_access_policy": "aibiDashboardEmbeddingAccessPolicy",
        "aibi_dashboard_embedding_approved_domains": "aibiDashboardEmbeddingApprovedDomains",
        "automatic_cluster_update_workspace": "automaticClusterUpdateWorkspace",
        "boolean_val": "booleanVal",
        "default_data_security_mode": "defaultDataSecurityMode",
        "effective_aibi_dashboard_embedding_access_policy": "effectiveAibiDashboardEmbeddingAccessPolicy",
        "effective_aibi_dashboard_embedding_approved_domains": "effectiveAibiDashboardEmbeddingApprovedDomains",
        "effective_automatic_cluster_update_workspace": "effectiveAutomaticClusterUpdateWorkspace",
        "effective_default_data_security_mode": "effectiveDefaultDataSecurityMode",
        "effective_personal_compute": "effectivePersonalCompute",
        "effective_restrict_workspace_admins": "effectiveRestrictWorkspaceAdmins",
        "integer_val": "integerVal",
        "name": "name",
        "personal_compute": "personalCompute",
        "restrict_workspace_admins": "restrictWorkspaceAdmins",
        "string_val": "stringVal",
    },
)
class AccountSettingV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union[AccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["AccountSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["AccountSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["AccountSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["AccountSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["AccountSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["AccountSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["AccountSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["AccountSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_access_policy AccountSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_approved_domains AccountSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#automatic_cluster_update_workspace AccountSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#boolean_val AccountSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#default_data_security_mode AccountSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy AccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains AccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_automatic_cluster_update_workspace AccountSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_default_data_security_mode AccountSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_personal_compute AccountSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_restrict_workspace_admins AccountSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#integer_val AccountSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#name AccountSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#personal_compute AccountSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restrict_workspace_admins AccountSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#string_val AccountSettingV2#string_val}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aibi_dashboard_embedding_access_policy, dict):
            aibi_dashboard_embedding_access_policy = AccountSettingV2AibiDashboardEmbeddingAccessPolicy(**aibi_dashboard_embedding_access_policy)
        if isinstance(aibi_dashboard_embedding_approved_domains, dict):
            aibi_dashboard_embedding_approved_domains = AccountSettingV2AibiDashboardEmbeddingApprovedDomains(**aibi_dashboard_embedding_approved_domains)
        if isinstance(automatic_cluster_update_workspace, dict):
            automatic_cluster_update_workspace = AccountSettingV2AutomaticClusterUpdateWorkspace(**automatic_cluster_update_workspace)
        if isinstance(boolean_val, dict):
            boolean_val = AccountSettingV2BooleanVal(**boolean_val)
        if isinstance(default_data_security_mode, dict):
            default_data_security_mode = AccountSettingV2DefaultDataSecurityMode(**default_data_security_mode)
        if isinstance(effective_aibi_dashboard_embedding_access_policy, dict):
            effective_aibi_dashboard_embedding_access_policy = AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(**effective_aibi_dashboard_embedding_access_policy)
        if isinstance(effective_aibi_dashboard_embedding_approved_domains, dict):
            effective_aibi_dashboard_embedding_approved_domains = AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(**effective_aibi_dashboard_embedding_approved_domains)
        if isinstance(effective_automatic_cluster_update_workspace, dict):
            effective_automatic_cluster_update_workspace = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(**effective_automatic_cluster_update_workspace)
        if isinstance(effective_default_data_security_mode, dict):
            effective_default_data_security_mode = AccountSettingV2EffectiveDefaultDataSecurityMode(**effective_default_data_security_mode)
        if isinstance(effective_personal_compute, dict):
            effective_personal_compute = AccountSettingV2EffectivePersonalCompute(**effective_personal_compute)
        if isinstance(effective_restrict_workspace_admins, dict):
            effective_restrict_workspace_admins = AccountSettingV2EffectiveRestrictWorkspaceAdmins(**effective_restrict_workspace_admins)
        if isinstance(integer_val, dict):
            integer_val = AccountSettingV2IntegerVal(**integer_val)
        if isinstance(personal_compute, dict):
            personal_compute = AccountSettingV2PersonalCompute(**personal_compute)
        if isinstance(restrict_workspace_admins, dict):
            restrict_workspace_admins = AccountSettingV2RestrictWorkspaceAdmins(**restrict_workspace_admins)
        if isinstance(string_val, dict):
            string_val = AccountSettingV2StringVal(**string_val)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ceedc900c5705cd9135555ee91ba28a38e67e9f32cdcf0c567cce55dd60c292)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument aibi_dashboard_embedding_access_policy", value=aibi_dashboard_embedding_access_policy, expected_type=type_hints["aibi_dashboard_embedding_access_policy"])
            check_type(argname="argument aibi_dashboard_embedding_approved_domains", value=aibi_dashboard_embedding_approved_domains, expected_type=type_hints["aibi_dashboard_embedding_approved_domains"])
            check_type(argname="argument automatic_cluster_update_workspace", value=automatic_cluster_update_workspace, expected_type=type_hints["automatic_cluster_update_workspace"])
            check_type(argname="argument boolean_val", value=boolean_val, expected_type=type_hints["boolean_val"])
            check_type(argname="argument default_data_security_mode", value=default_data_security_mode, expected_type=type_hints["default_data_security_mode"])
            check_type(argname="argument effective_aibi_dashboard_embedding_access_policy", value=effective_aibi_dashboard_embedding_access_policy, expected_type=type_hints["effective_aibi_dashboard_embedding_access_policy"])
            check_type(argname="argument effective_aibi_dashboard_embedding_approved_domains", value=effective_aibi_dashboard_embedding_approved_domains, expected_type=type_hints["effective_aibi_dashboard_embedding_approved_domains"])
            check_type(argname="argument effective_automatic_cluster_update_workspace", value=effective_automatic_cluster_update_workspace, expected_type=type_hints["effective_automatic_cluster_update_workspace"])
            check_type(argname="argument effective_default_data_security_mode", value=effective_default_data_security_mode, expected_type=type_hints["effective_default_data_security_mode"])
            check_type(argname="argument effective_personal_compute", value=effective_personal_compute, expected_type=type_hints["effective_personal_compute"])
            check_type(argname="argument effective_restrict_workspace_admins", value=effective_restrict_workspace_admins, expected_type=type_hints["effective_restrict_workspace_admins"])
            check_type(argname="argument integer_val", value=integer_val, expected_type=type_hints["integer_val"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument personal_compute", value=personal_compute, expected_type=type_hints["personal_compute"])
            check_type(argname="argument restrict_workspace_admins", value=restrict_workspace_admins, expected_type=type_hints["restrict_workspace_admins"])
            check_type(argname="argument string_val", value=string_val, expected_type=type_hints["string_val"])
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
        if aibi_dashboard_embedding_access_policy is not None:
            self._values["aibi_dashboard_embedding_access_policy"] = aibi_dashboard_embedding_access_policy
        if aibi_dashboard_embedding_approved_domains is not None:
            self._values["aibi_dashboard_embedding_approved_domains"] = aibi_dashboard_embedding_approved_domains
        if automatic_cluster_update_workspace is not None:
            self._values["automatic_cluster_update_workspace"] = automatic_cluster_update_workspace
        if boolean_val is not None:
            self._values["boolean_val"] = boolean_val
        if default_data_security_mode is not None:
            self._values["default_data_security_mode"] = default_data_security_mode
        if effective_aibi_dashboard_embedding_access_policy is not None:
            self._values["effective_aibi_dashboard_embedding_access_policy"] = effective_aibi_dashboard_embedding_access_policy
        if effective_aibi_dashboard_embedding_approved_domains is not None:
            self._values["effective_aibi_dashboard_embedding_approved_domains"] = effective_aibi_dashboard_embedding_approved_domains
        if effective_automatic_cluster_update_workspace is not None:
            self._values["effective_automatic_cluster_update_workspace"] = effective_automatic_cluster_update_workspace
        if effective_default_data_security_mode is not None:
            self._values["effective_default_data_security_mode"] = effective_default_data_security_mode
        if effective_personal_compute is not None:
            self._values["effective_personal_compute"] = effective_personal_compute
        if effective_restrict_workspace_admins is not None:
            self._values["effective_restrict_workspace_admins"] = effective_restrict_workspace_admins
        if integer_val is not None:
            self._values["integer_val"] = integer_val
        if name is not None:
            self._values["name"] = name
        if personal_compute is not None:
            self._values["personal_compute"] = personal_compute
        if restrict_workspace_admins is not None:
            self._values["restrict_workspace_admins"] = restrict_workspace_admins
        if string_val is not None:
            self._values["string_val"] = string_val

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
    def aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional[AccountSettingV2AibiDashboardEmbeddingAccessPolicy]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_access_policy AccountSettingV2#aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional[AccountSettingV2AibiDashboardEmbeddingAccessPolicy], result)

    @builtins.property
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional[AccountSettingV2AibiDashboardEmbeddingApprovedDomains]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#aibi_dashboard_embedding_approved_domains AccountSettingV2#aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional[AccountSettingV2AibiDashboardEmbeddingApprovedDomains], result)

    @builtins.property
    def automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional[AccountSettingV2AutomaticClusterUpdateWorkspace]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#automatic_cluster_update_workspace AccountSettingV2#automatic_cluster_update_workspace}.'''
        result = self._values.get("automatic_cluster_update_workspace")
        return typing.cast(typing.Optional[AccountSettingV2AutomaticClusterUpdateWorkspace], result)

    @builtins.property
    def boolean_val(self) -> typing.Optional[AccountSettingV2BooleanVal]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#boolean_val AccountSettingV2#boolean_val}.'''
        result = self._values.get("boolean_val")
        return typing.cast(typing.Optional[AccountSettingV2BooleanVal], result)

    @builtins.property
    def default_data_security_mode(
        self,
    ) -> typing.Optional["AccountSettingV2DefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#default_data_security_mode AccountSettingV2#default_data_security_mode}.'''
        result = self._values.get("default_data_security_mode")
        return typing.cast(typing.Optional["AccountSettingV2DefaultDataSecurityMode"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy AccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains AccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"], result)

    @builtins.property
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_automatic_cluster_update_workspace AccountSettingV2#effective_automatic_cluster_update_workspace}.'''
        result = self._values.get("effective_automatic_cluster_update_workspace")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"], result)

    @builtins.property
    def effective_default_data_security_mode(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveDefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_default_data_security_mode AccountSettingV2#effective_default_data_security_mode}.'''
        result = self._values.get("effective_default_data_security_mode")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveDefaultDataSecurityMode"], result)

    @builtins.property
    def effective_personal_compute(
        self,
    ) -> typing.Optional["AccountSettingV2EffectivePersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_personal_compute AccountSettingV2#effective_personal_compute}.'''
        result = self._values.get("effective_personal_compute")
        return typing.cast(typing.Optional["AccountSettingV2EffectivePersonalCompute"], result)

    @builtins.property
    def effective_restrict_workspace_admins(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveRestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#effective_restrict_workspace_admins AccountSettingV2#effective_restrict_workspace_admins}.'''
        result = self._values.get("effective_restrict_workspace_admins")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveRestrictWorkspaceAdmins"], result)

    @builtins.property
    def integer_val(self) -> typing.Optional["AccountSettingV2IntegerVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#integer_val AccountSettingV2#integer_val}.'''
        result = self._values.get("integer_val")
        return typing.cast(typing.Optional["AccountSettingV2IntegerVal"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#name AccountSettingV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personal_compute(self) -> typing.Optional["AccountSettingV2PersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#personal_compute AccountSettingV2#personal_compute}.'''
        result = self._values.get("personal_compute")
        return typing.cast(typing.Optional["AccountSettingV2PersonalCompute"], result)

    @builtins.property
    def restrict_workspace_admins(
        self,
    ) -> typing.Optional["AccountSettingV2RestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restrict_workspace_admins AccountSettingV2#restrict_workspace_admins}.'''
        result = self._values.get("restrict_workspace_admins")
        return typing.cast(typing.Optional["AccountSettingV2RestrictWorkspaceAdmins"], result)

    @builtins.property
    def string_val(self) -> typing.Optional["AccountSettingV2StringVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#string_val AccountSettingV2#string_val}.'''
        result = self._values.get("string_val")
        return typing.cast(typing.Optional["AccountSettingV2StringVal"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2DefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class AccountSettingV2DefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36f17dd1e7df8ab344e6b60653a920ec03c346bdb542e5c00751148a7f9f9685)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2DefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2DefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2DefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__37c2919aa148ab11b77d348008746ab2fc321459ba25fdd783b1b6ad3fc3aea3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96b39694ed9509704cb11562cab0373095663e334f7a1076e22e7252cb0c9d00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2DefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2DefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2DefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b373bbbb2aceadc2fec42b7270bfe2f30c916a7523ba036ab6d1d3a4348a76c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c7a3678d1c3d686b631dc87a29d4a798c5474117f8af07af45e0cd399c1bb15)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#access_policy_type AccountSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__495f58c38a5a849f4312aaa6540d1341d4c1df9207d462c8f617d5ed1dda0fbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="accessPolicyTypeInput")
    def access_policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPolicyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="accessPolicyType")
    def access_policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPolicyType"))

    @access_policy_type.setter
    def access_policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07b2511fe1c4d3e22f965bd41a149f55e5884beae6a913ad25be2306c6c7c9da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd81902c6b3630d1def82769f3320e4c142fb5c270e38c108625b1f9dc5e8179)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4230e23733569539674af0132a763ca574c7d485eb550035d9fa1b4f1a9d7b2e)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#approved_domains AccountSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__086c239d6efe83be46622b5901d6f5ffec353b3aad6692f3119ee5c73cf47f17)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetApprovedDomains")
    def reset_approved_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApprovedDomains", []))

    @builtins.property
    @jsii.member(jsii_name="approvedDomainsInput")
    def approved_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "approvedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="approvedDomains")
    def approved_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "approvedDomains"))

    @approved_domains.setter
    def approved_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d354b6e80c5385412fa5bca7510d85bb1caa86b634e6861c5992c737d3ff0688)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1128faa48ab67555e4eb7ec23f5748aad7a8b8e03eb30e3226042af8b59bfd05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a705c76dc3c0af595a4f3508fb02ff11959d2693ad40d4befdcbbbfa50d8013)
            check_type(argname="argument can_toggle", value=can_toggle, expected_type=type_hints["can_toggle"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument enablement_details", value=enablement_details, expected_type=type_hints["enablement_details"])
            check_type(argname="argument maintenance_window", value=maintenance_window, expected_type=type_hints["maintenance_window"])
            check_type(argname="argument restart_even_if_no_updates_available", value=restart_even_if_no_updates_available, expected_type=type_hints["restart_even_if_no_updates_available"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if can_toggle is not None:
            self._values["can_toggle"] = can_toggle
        if enabled is not None:
            self._values["enabled"] = enabled
        if enablement_details is not None:
            self._values["enablement_details"] = enablement_details
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if restart_even_if_no_updates_available is not None:
            self._values["restart_even_if_no_updates_available"] = restart_even_if_no_updates_available

    @builtins.property
    def can_toggle(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#can_toggle AccountSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enabled AccountSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#enablement_details AccountSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#maintenance_window AccountSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#restart_even_if_no_updates_available AccountSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfecabf1a39dc8e617b532402c703229519122b85ea5f490c1178ec2569d88ba)
            check_type(argname="argument forced_for_compliance_mode", value=forced_for_compliance_mode, expected_type=type_hints["forced_for_compliance_mode"])
            check_type(argname="argument unavailable_for_disabled_entitlement", value=unavailable_for_disabled_entitlement, expected_type=type_hints["unavailable_for_disabled_entitlement"])
            check_type(argname="argument unavailable_for_non_enterprise_tier", value=unavailable_for_non_enterprise_tier, expected_type=type_hints["unavailable_for_non_enterprise_tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if forced_for_compliance_mode is not None:
            self._values["forced_for_compliance_mode"] = forced_for_compliance_mode
        if unavailable_for_disabled_entitlement is not None:
            self._values["unavailable_for_disabled_entitlement"] = unavailable_for_disabled_entitlement
        if unavailable_for_non_enterprise_tier is not None:
            self._values["unavailable_for_non_enterprise_tier"] = unavailable_for_non_enterprise_tier

    @builtins.property
    def forced_for_compliance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c85686e09dcb6c5b22bfa7cc907b603757b67aa60e5c0a1f52be4466f5f8d6b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetForcedForComplianceMode")
    def reset_forced_for_compliance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForcedForComplianceMode", []))

    @jsii.member(jsii_name="resetUnavailableForDisabledEntitlement")
    def reset_unavailable_for_disabled_entitlement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForDisabledEntitlement", []))

    @jsii.member(jsii_name="resetUnavailableForNonEnterpriseTier")
    def reset_unavailable_for_non_enterprise_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnavailableForNonEnterpriseTier", []))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceModeInput")
    def forced_for_compliance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forcedForComplianceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlementInput")
    def unavailable_for_disabled_entitlement_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForDisabledEntitlementInput"))

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTierInput")
    def unavailable_for_non_enterprise_tier_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unavailableForNonEnterpriseTierInput"))

    @builtins.property
    @jsii.member(jsii_name="forcedForComplianceMode")
    def forced_for_compliance_mode(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forcedForComplianceMode"))

    @forced_for_compliance_mode.setter
    def forced_for_compliance_mode(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e12f07ac41354c1b5155ebf750433bb97ecc9ded939103888c71d112d2805aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forcedForComplianceMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unavailableForDisabledEntitlement")
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForDisabledEntitlement"))

    @unavailable_for_disabled_entitlement.setter
    def unavailable_for_disabled_entitlement(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5ea1b6abef23378d2fdd14a91b86942100908f3193536720e23dcf5c4837df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForDisabledEntitlement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unavailableForNonEnterpriseTier")
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unavailableForNonEnterpriseTier"))

    @unavailable_for_non_enterprise_tier.setter
    def unavailable_for_non_enterprise_tier(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5604b96b8518caddd3e5a19419a791c45f5916b647052df2634b76101b58c557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2688bd6b56cb4761c7f76bf41cccceb1527e3b8ec80ae9c487dec8ce57eee4ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15c4cc47c69d91af7094b4100876fdf166429d1bbbe20d3fd2d1efcd128bc1f1)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3b83241363bf2af50b5d41f2c7dbd006f09bad81257a97b4758632bab3badf3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.
        '''
        value = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
            day_of_week=day_of_week,
            frequency=frequency,
            window_start_time=window_start_time,
        )

        return typing.cast(None, jsii.invoke(self, "putWeekDayBasedSchedule", [value]))

    @jsii.member(jsii_name="resetWeekDayBasedSchedule")
    def reset_week_day_based_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeekDayBasedSchedule", []))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedSchedule")
    def week_day_based_schedule(
        self,
    ) -> "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd9e2c96cef8fcdffc89e883e182d2a2f55bfe99bcedd8281f9b6983e8fa963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__645c43041dbfae0f8243a54dcefc5822e4486f420ec08ec09c07d8552f03afa8)
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument window_start_time", value=window_start_time, expected_type=type_hints["window_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day_of_week is not None:
            self._values["day_of_week"] = day_of_week
        if frequency is not None:
            self._values["frequency"] = frequency
        if window_start_time is not None:
            self._values["window_start_time"] = window_start_time

    @builtins.property
    def day_of_week(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#day_of_week AccountSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#frequency AccountSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#window_start_time AccountSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__77c9cd8aefa33bc03ffb59bebeaba9e74cd74a4c0389abac9ee416e515b8dc68)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWindowStartTime")
    def put_window_start_time(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.
        '''
        value = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
            hours=hours, minutes=minutes
        )

        return typing.cast(None, jsii.invoke(self, "putWindowStartTime", [value]))

    @jsii.member(jsii_name="resetDayOfWeek")
    def reset_day_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDayOfWeek", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetWindowStartTime")
    def reset_window_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowStartTime", []))

    @builtins.property
    @jsii.member(jsii_name="windowStartTime")
    def window_start_time(
        self,
    ) -> "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property
    @jsii.member(jsii_name="windowStartTimeInput")
    def window_start_time_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a4788803ca7204fc4a24369987f20c7a1432fe2f7f6f666d9157f3168bfe26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f026e27b89056d26fd2881dd5ca117162bec684fc91b1c56216d5edd8cd52032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dd09c37fc50495c69be8c892f8df8ba7ff3eec923a77f21b742ec92dd22112a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c051f39842664de44d3d0651247a2800f2f53ab39dc59858b7a44f6969d54ce4)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#hours AccountSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#minutes AccountSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__524e5a52153962808076248db4a74fd54dbc4f9c491fefeb5acef4c1730953cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHours")
    def reset_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHours", []))

    @jsii.member(jsii_name="resetMinutes")
    def reset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinutes", []))

    @builtins.property
    @jsii.member(jsii_name="hoursInput")
    def hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hoursInput"))

    @builtins.property
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property
    @jsii.member(jsii_name="hours")
    def hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hours"))

    @hours.setter
    def hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18cf3faf5a05123d4e23ca731341bf873475f1c15938936913cd2be1373c2a12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68908c3b9bbd929df66c24503b91d1f8a3ed354fb229eb1c47bab1fe51a3a1da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e163f28855d05be24783f090bece50a960378ee3e6d018624ce013b4f960db85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5913ab9da6a35d0edc9f7a04998bbef1c40f3bda541f730eb7b7c603f2389a16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEnablementDetails")
    def put_enablement_details(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#forced_for_compliance_mode AccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_disabled_entitlement AccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#unavailable_for_non_enterprise_tier AccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#week_day_based_schedule AccountSettingV2#week_day_based_schedule}.
        '''
        value = AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(
            week_day_based_schedule=week_day_based_schedule
        )

        return typing.cast(None, jsii.invoke(self, "putMaintenanceWindow", [value]))

    @jsii.member(jsii_name="resetCanToggle")
    def reset_can_toggle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanToggle", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnablementDetails")
    def reset_enablement_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablementDetails", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetRestartEvenIfNoUpdatesAvailable")
    def reset_restart_even_if_no_updates_available(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartEvenIfNoUpdatesAvailable", []))

    @builtins.property
    @jsii.member(jsii_name="enablementDetails")
    def enablement_details(
        self,
    ) -> AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

    @builtins.property
    @jsii.member(jsii_name="canToggleInput")
    def can_toggle_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "canToggleInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enablementDetailsInput")
    def enablement_details_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailableInput")
    def restart_even_if_no_updates_available_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "restartEvenIfNoUpdatesAvailableInput"))

    @builtins.property
    @jsii.member(jsii_name="canToggle")
    def can_toggle(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "canToggle"))

    @can_toggle.setter
    def can_toggle(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__923aa8027727074f2b793940ae2697ead2d52fa28b28a4b2e3a5b358c4c97670)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canToggle", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__4394b4d8edea37293de0db08919cfd0eca03fbc9d3ec5277cea6db3622adc517)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restartEvenIfNoUpdatesAvailable")
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "restartEvenIfNoUpdatesAvailable"))

    @restart_even_if_no_updates_available.setter
    def restart_even_if_no_updates_available(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026726abaa2ed5c25bb17dfe70bc6be89947f042928247a9b6fa948f55a63080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03aea900f0a867cb0389f09ca8986230e0009badb856285df3c5c1acc7ec817c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveBooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2EffectiveBooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4886d54e4193ef9e89886fbe1bcffed67ad1adaa0619446c7718625385b13e3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveBooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveBooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveBooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10bd456d858fc78c7bddb53542ab533ad0f8f40c099bb03c4c0a344eff7ed042)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "value"))

    @value.setter
    def value(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5c64d39257d98322221128aa8a44f0222d2bdd500e86033db8c1f45ec9823ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AccountSettingV2EffectiveBooleanVal]:
        return typing.cast(typing.Optional[AccountSettingV2EffectiveBooleanVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AccountSettingV2EffectiveBooleanVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__485de62576d30c1682c38483b9412c7066ff4c203547841e645a36c53d24bff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveDefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class AccountSettingV2EffectiveDefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58ffdc16a1cc2d8acd98be595afb878873ce15043d35c6e8d71ebd126e7f13c5)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveDefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveDefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveDefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54061992b8b358cd05d2dc0aae6510be42247e5cd199491d0ade01dd598ed45e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b5479c77c5ed9ac51f3ed362829ccb160508ec4ff8ca5f7a361cc2d519a4662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveDefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveDefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveDefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcca982e81ea8d8838917f79049e8adc67a02c30d4e6728d766f222a49533bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveIntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2EffectiveIntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c68b37b0c738c652a8c091ffb1ed2a96679c1f9e4a53951b3dc08ef942a39017)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveIntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveIntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveIntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6a57f354853f826eb4b4ad57f4da55b45424ce2f49a8ed49275679adc46473f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e012e6797f0dfffa93d65db8c681ca1ca029b14e07bce571c3bdca95a193ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AccountSettingV2EffectiveIntegerVal]:
        return typing.cast(typing.Optional[AccountSettingV2EffectiveIntegerVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AccountSettingV2EffectiveIntegerVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d86a10076201bd72492d3485f2d6fef32263009ba8711d80957921ab8112cc56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectivePersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2EffectivePersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d30696df46a78df890321d5d3d39ce475959d2af8d7e6163c3b5075fa67b05e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectivePersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectivePersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectivePersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9d42f8195850eb673a80d5e6460ef7b808258221cd5195dde14d57424f36fb4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9d2184967e6b8f0960296333be7274c797376b95db55ea603883ebe0140222c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectivePersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectivePersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectivePersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c6d8cca166012f4d84493e9fe505d82b6d548b3262714fa3262f1cfa055a23d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveRestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class AccountSettingV2EffectiveRestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ccec347c0662e2181690d8523625a45e7ec82aefc0fcab548cb76f3c87b68f)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveRestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__662258fc523402d6807f4445aa911521399596ad8e92de8573c03a1da8f4c6e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6aeb10b1868825fb0b4b4e44945ef898f48cc6070eaacd20d8595ec18d985e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveRestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveRestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveRestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__148e0a93ef5f259aeef1ed227d7d56cdefa2d5cfae2a41420c3224c8a83fbaad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveStringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2EffectiveStringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd56a50b43d235d63577e8defbe951b1378566ba071a2e002347d162f35d421)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2EffectiveStringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2EffectiveStringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2EffectiveStringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dd0d7f6e6d3672f84487ddf3d2a4b219becf591700211496af9621a180b67d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9a8ded4b7177bb23bfd6f8018babf032344b9dafa66325531ebcd4110dcb915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AccountSettingV2EffectiveStringVal]:
        return typing.cast(typing.Optional[AccountSettingV2EffectiveStringVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AccountSettingV2EffectiveStringVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec649d6c87742b14062973d658123749df9205c6e9f89219f8bed97a3e501363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2IntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2IntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a0483868c06afd7cc881313e12d19e9583928191e7dd6e9c73f69a5a26e12d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2IntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2IntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2IntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2f0f78582f121e24e0ac68b1cb9d6e9e91199e4ede436f284740ecc90ae0721)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bfe68861d34e653d3560f759640530d4b1c9ef55e1cf144e7df25fd758d26cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2IntegerVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2IntegerVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2IntegerVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21438cdd994ebe89b65e1eeece9ba069d51139c9fe19a3ed12baa573525d9187)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2PersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2PersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d600d801bdb56aef33b68101ef5e47e3830006ee6e1f9bd718898992def627b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2PersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2PersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2PersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4aea872d983cbc774cbbe60e9cb0c15a93b7d5a2e1d924c0618237a8f5c83615)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__757f7845dcc6dad5491a742f2459555e3931d4b2ef98f8092afefd1698f70146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2PersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2PersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2PersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__978e78033f2100d52ffccf96fa8e5dc3f28260c7bbc8ef08585bfa5132e8aa0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2RestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class AccountSettingV2RestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8390b837b66ae53c3c137d8cd930ae69b6f3546251cbcc0f4af78cb12bdbf48)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#status AccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2RestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2RestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2RestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce0d43c0c275bf5ee2974a8a4a5fec7935bfe6c761cbad177670ec5a290e3f03)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af5fcab1ba907681294d8a2e969ad157a2219645fbedbbccfe2e35f04b2cb327)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2RestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2RestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2RestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd3edc83793227ddc8964a3a27a37325b494fc5806e2c4449e45c6beab1c8f74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2StringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class AccountSettingV2StringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5419269787316dc5e7253beb437b116f33a659f6f6f65c15ecac04d4795a19d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/account_setting_v2#value AccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountSettingV2StringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccountSettingV2StringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.accountSettingV2.AccountSettingV2StringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46a7e1700d9434bbd1565383e7271314be08cb239685a3b8c77587bec95faae5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c494ce9d05c21ad98ac0eb5383eef45d7176157b826c02e3e1dd4e356367f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2StringVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2StringVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2StringVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30906c0873e351e3089d9e1b7a7a20e72132d6364941a7bd3d4c3c730ae9eb13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AccountSettingV2",
    "AccountSettingV2AibiDashboardEmbeddingAccessPolicy",
    "AccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
    "AccountSettingV2AibiDashboardEmbeddingApprovedDomains",
    "AccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
    "AccountSettingV2AutomaticClusterUpdateWorkspace",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "AccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
    "AccountSettingV2BooleanVal",
    "AccountSettingV2BooleanValOutputReference",
    "AccountSettingV2Config",
    "AccountSettingV2DefaultDataSecurityMode",
    "AccountSettingV2DefaultDataSecurityModeOutputReference",
    "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    "AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
    "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    "AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
    "AccountSettingV2EffectiveBooleanVal",
    "AccountSettingV2EffectiveBooleanValOutputReference",
    "AccountSettingV2EffectiveDefaultDataSecurityMode",
    "AccountSettingV2EffectiveDefaultDataSecurityModeOutputReference",
    "AccountSettingV2EffectiveIntegerVal",
    "AccountSettingV2EffectiveIntegerValOutputReference",
    "AccountSettingV2EffectivePersonalCompute",
    "AccountSettingV2EffectivePersonalComputeOutputReference",
    "AccountSettingV2EffectiveRestrictWorkspaceAdmins",
    "AccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
    "AccountSettingV2EffectiveStringVal",
    "AccountSettingV2EffectiveStringValOutputReference",
    "AccountSettingV2IntegerVal",
    "AccountSettingV2IntegerValOutputReference",
    "AccountSettingV2PersonalCompute",
    "AccountSettingV2PersonalComputeOutputReference",
    "AccountSettingV2RestrictWorkspaceAdmins",
    "AccountSettingV2RestrictWorkspaceAdminsOutputReference",
    "AccountSettingV2StringVal",
    "AccountSettingV2StringValOutputReference",
]

publication.publish()

def _typecheckingstub__05440c638d02a166d37692133a522e493cd3fa6f257e124ad65b1b7a8b6edf65(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[AccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[AccountSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[AccountSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[AccountSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[AccountSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[AccountSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[AccountSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[AccountSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[AccountSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__0e8d3b5edd4077e29d08f40f6f387cc0fdafcf7e79365b96281976564e9a64dc(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ccc01b884abb530e85ebbcd25c8b068b1d766514363f6ac019b08daea61b2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3140b4aee6c2d40283b7a42c4f3ba3f1958f97f730788b93bcf6d66e7e9cf5b3(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f61a1cdf785b3513cc978b8a0cfd54582033706eb5164c1512692fb45dfafd5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__540dcfbb590b9e55dfe72cfb537c548d61fc4c49e896a92c5398f6d1768220b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51782d718040e5ca57e255bf4863bbd7501a9c505c57f907f3c80ee47e629bce(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__088616014d0dd80119e5f525574a5ab5980b13dd892eea385aec3d4983e25393(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50e4d0f887403a965f6dd573376976c6cf8a0113452004fef2159cf69108d0ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6395529b0a90617c37f11f558ca4fa3b9ecb7d47229ecd795ad7d89b762ce89(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0098dcb7758a9f1772a633f3c61bfe9ddd740537c363bf4e0630685fa72eff72(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12370d75cdcaaa38e41b65431ebb0159ec940c9f8ef673542eb5969f55b87def(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb524cad5b281cff1b9c7aab60aa8e0e501573cc0f6a6798a3fa16741816e79(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__015da414e8f306d01f13612a7b546dc3a2982145449f94e2e42806aa550b1e8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eea0e98008b365a0b4d59ac618fc9b535fe188b9979e5785559b265db2d1d4a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8583d3c67fca45cb7085efe53ce08053e2daa690f4a90abbf530514a00a154(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7531c182aeab7309cd317d914ba839c84465fd2daeb3461209ee18c7eb4fbc21(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c73c53049f192ef13d0008d5848db36ee38dc04d2179f959ce0e8a57df9edbd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0638f7ad8f66d17347ba4f11f952f624a7e8e1a806988b76729980d1a5ef13a4(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__832fcf26b16ff0c89196897a899866fbaacae6c2931b7f6275cb8cea6f871ff2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa56845b772c4e30e650dd7ee768c8d5ebffa424ad7e708c329a4f8f3401f1c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b43491c365ee54d91fe9cc401fe4b7e3c1603ea8ca9acae4444137643e0ba77(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f099a6eeebf327cf708367ae1c530f5884dba46ef5a1f14cf23b8e902ed3ce91(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17cf2a848ae24e8ef9891cd99dd16a942691aa0ba8c9a294b147ed84cee34f4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__693da47f83d3accb0df97721818d3fa1099aab22ce89928959494ed25a2055b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a07928397134c32f678c719805c33e5c93f14e35958a61cb7b129676814a6a9a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c04054b0bc67f163119c78311193a1130005ae83a386f68ad976c22a0d8459(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e56fa5f4432692a3f0f5a8fbbdfc7fedafdee07fcbaba51d57de9663a2b69586(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d438d0e8cedbd80f4ae03a8163f4332b9722a334724a7455eea0e4402ec7edd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__235a49a1f7dfd61ae8a35b85581337fb1c54e0b571b9d8c52a303b89330d944b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9477b4fdbd39cefa8cb8caaec2196bb8b565e5efaf1bdaecf761e581e6cdcbd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c5e1aeda3dac627c8e5b3651443946372547d883d4223e649f13cab1e0cab2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55c3cd6552d8994987aa6d1482757fb4b256d157ab29e59c12a65190aa8f9e42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf3ee418953deb220ce9eda992b0ce7593a6d3f162084416d1c29fd64e4b21ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83e54086f4fda010ea2370d9de00a2fd602a4a5f5c88b287c9b530509de3ce8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26699902ff95b76c35bb8e801c91582a31f7fbbc78115aa7c88355f2a9e7117d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2AutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb451bac3ed4cb8034da33a42ad301f2f886eb23ccf7b8fb6f060724221a109f(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e73a11a7b01146e28100c0d4b0c528aa5e10cd0ef4a1556b42f5340f8559fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f730cd1c39c62370a9b582466a24bd16269f261ad02cadd8736bb8fde4eaea(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e08b0fd3edb59e476dd2ec47f698da8717a8fb5723d440a88d1cc308b57909f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2BooleanVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ceedc900c5705cd9135555ee91ba28a38e67e9f32cdcf0c567cce55dd60c292(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[AccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[AccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[AccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[AccountSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[AccountSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[AccountSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[AccountSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[AccountSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[AccountSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[AccountSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[AccountSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36f17dd1e7df8ab344e6b60653a920ec03c346bdb542e5c00751148a7f9f9685(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37c2919aa148ab11b77d348008746ab2fc321459ba25fdd783b1b6ad3fc3aea3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96b39694ed9509704cb11562cab0373095663e334f7a1076e22e7252cb0c9d00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b373bbbb2aceadc2fec42b7270bfe2f30c916a7523ba036ab6d1d3a4348a76c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2DefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c7a3678d1c3d686b631dc87a29d4a798c5474117f8af07af45e0cd399c1bb15(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__495f58c38a5a849f4312aaa6540d1341d4c1df9207d462c8f617d5ed1dda0fbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07b2511fe1c4d3e22f965bd41a149f55e5884beae6a913ad25be2306c6c7c9da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd81902c6b3630d1def82769f3320e4c142fb5c270e38c108625b1f9dc5e8179(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4230e23733569539674af0132a763ca574c7d485eb550035d9fa1b4f1a9d7b2e(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__086c239d6efe83be46622b5901d6f5ffec353b3aad6692f3119ee5c73cf47f17(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d354b6e80c5385412fa5bca7510d85bb1caa86b634e6861c5992c737d3ff0688(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1128faa48ab67555e4eb7ec23f5748aad7a8b8e03eb30e3226042af8b59bfd05(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a705c76dc3c0af595a4f3508fb02ff11959d2693ad40d4befdcbbbfa50d8013(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfecabf1a39dc8e617b532402c703229519122b85ea5f490c1178ec2569d88ba(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c85686e09dcb6c5b22bfa7cc907b603757b67aa60e5c0a1f52be4466f5f8d6b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e12f07ac41354c1b5155ebf750433bb97ecc9ded939103888c71d112d2805aa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5ea1b6abef23378d2fdd14a91b86942100908f3193536720e23dcf5c4837df(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5604b96b8518caddd3e5a19419a791c45f5916b647052df2634b76101b58c557(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2688bd6b56cb4761c7f76bf41cccceb1527e3b8ec80ae9c487dec8ce57eee4ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15c4cc47c69d91af7094b4100876fdf166429d1bbbe20d3fd2d1efcd128bc1f1(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b83241363bf2af50b5d41f2c7dbd006f09bad81257a97b4758632bab3badf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd9e2c96cef8fcdffc89e883e182d2a2f55bfe99bcedd8281f9b6983e8fa963(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__645c43041dbfae0f8243a54dcefc5822e4486f420ec08ec09c07d8552f03afa8(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77c9cd8aefa33bc03ffb59bebeaba9e74cd74a4c0389abac9ee416e515b8dc68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a4788803ca7204fc4a24369987f20c7a1432fe2f7f6f666d9157f3168bfe26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f026e27b89056d26fd2881dd5ca117162bec684fc91b1c56216d5edd8cd52032(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dd09c37fc50495c69be8c892f8df8ba7ff3eec923a77f21b742ec92dd22112a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c051f39842664de44d3d0651247a2800f2f53ab39dc59858b7a44f6969d54ce4(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524e5a52153962808076248db4a74fd54dbc4f9c491fefeb5acef4c1730953cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18cf3faf5a05123d4e23ca731341bf873475f1c15938936913cd2be1373c2a12(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68908c3b9bbd929df66c24503b91d1f8a3ed354fb229eb1c47bab1fe51a3a1da(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e163f28855d05be24783f090bece50a960378ee3e6d018624ce013b4f960db85(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5913ab9da6a35d0edc9f7a04998bbef1c40f3bda541f730eb7b7c603f2389a16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__923aa8027727074f2b793940ae2697ead2d52fa28b28a4b2e3a5b358c4c97670(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4394b4d8edea37293de0db08919cfd0eca03fbc9d3ec5277cea6db3622adc517(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026726abaa2ed5c25bb17dfe70bc6be89947f042928247a9b6fa948f55a63080(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03aea900f0a867cb0389f09ca8986230e0009badb856285df3c5c1acc7ec817c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4886d54e4193ef9e89886fbe1bcffed67ad1adaa0619446c7718625385b13e3d(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10bd456d858fc78c7bddb53542ab533ad0f8f40c099bb03c4c0a344eff7ed042(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c64d39257d98322221128aa8a44f0222d2bdd500e86033db8c1f45ec9823ff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__485de62576d30c1682c38483b9412c7066ff4c203547841e645a36c53d24bff4(
    value: typing.Optional[AccountSettingV2EffectiveBooleanVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58ffdc16a1cc2d8acd98be595afb878873ce15043d35c6e8d71ebd126e7f13c5(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54061992b8b358cd05d2dc0aae6510be42247e5cd199491d0ade01dd598ed45e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b5479c77c5ed9ac51f3ed362829ccb160508ec4ff8ca5f7a361cc2d519a4662(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcca982e81ea8d8838917f79049e8adc67a02c30d4e6728d766f222a49533bef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveDefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c68b37b0c738c652a8c091ffb1ed2a96679c1f9e4a53951b3dc08ef942a39017(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6a57f354853f826eb4b4ad57f4da55b45424ce2f49a8ed49275679adc46473f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e012e6797f0dfffa93d65db8c681ca1ca029b14e07bce571c3bdca95a193ed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d86a10076201bd72492d3485f2d6fef32263009ba8711d80957921ab8112cc56(
    value: typing.Optional[AccountSettingV2EffectiveIntegerVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d30696df46a78df890321d5d3d39ce475959d2af8d7e6163c3b5075fa67b05e(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9d42f8195850eb673a80d5e6460ef7b808258221cd5195dde14d57424f36fb4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9d2184967e6b8f0960296333be7274c797376b95db55ea603883ebe0140222c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c6d8cca166012f4d84493e9fe505d82b6d548b3262714fa3262f1cfa055a23d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectivePersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ccec347c0662e2181690d8523625a45e7ec82aefc0fcab548cb76f3c87b68f(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__662258fc523402d6807f4445aa911521399596ad8e92de8573c03a1da8f4c6e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6aeb10b1868825fb0b4b4e44945ef898f48cc6070eaacd20d8595ec18d985e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__148e0a93ef5f259aeef1ed227d7d56cdefa2d5cfae2a41420c3224c8a83fbaad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2EffectiveRestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd56a50b43d235d63577e8defbe951b1378566ba071a2e002347d162f35d421(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dd0d7f6e6d3672f84487ddf3d2a4b219becf591700211496af9621a180b67d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9a8ded4b7177bb23bfd6f8018babf032344b9dafa66325531ebcd4110dcb915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec649d6c87742b14062973d658123749df9205c6e9f89219f8bed97a3e501363(
    value: typing.Optional[AccountSettingV2EffectiveStringVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a0483868c06afd7cc881313e12d19e9583928191e7dd6e9c73f69a5a26e12d0(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f0f78582f121e24e0ac68b1cb9d6e9e91199e4ede436f284740ecc90ae0721(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bfe68861d34e653d3560f759640530d4b1c9ef55e1cf144e7df25fd758d26cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21438cdd994ebe89b65e1eeece9ba069d51139c9fe19a3ed12baa573525d9187(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2IntegerVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d600d801bdb56aef33b68101ef5e47e3830006ee6e1f9bd718898992def627b(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aea872d983cbc774cbbe60e9cb0c15a93b7d5a2e1d924c0618237a8f5c83615(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__757f7845dcc6dad5491a742f2459555e3931d4b2ef98f8092afefd1698f70146(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__978e78033f2100d52ffccf96fa8e5dc3f28260c7bbc8ef08585bfa5132e8aa0f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2PersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8390b837b66ae53c3c137d8cd930ae69b6f3546251cbcc0f4af78cb12bdbf48(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0d43c0c275bf5ee2974a8a4a5fec7935bfe6c761cbad177670ec5a290e3f03(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5fcab1ba907681294d8a2e969ad157a2219645fbedbbccfe2e35f04b2cb327(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd3edc83793227ddc8964a3a27a37325b494fc5806e2c4449e45c6beab1c8f74(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2RestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5419269787316dc5e7253beb437b116f33a659f6f6f65c15ecac04d4795a19d(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46a7e1700d9434bbd1565383e7271314be08cb239685a3b8c77587bec95faae5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c494ce9d05c21ad98ac0eb5383eef45d7176157b826c02e3e1dd4e356367f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30906c0873e351e3089d9e1b7a7a20e72132d6364941a7bd3d4c3c730ae9eb13(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AccountSettingV2StringVal]],
) -> None:
    """Type checking stubs"""
    pass
