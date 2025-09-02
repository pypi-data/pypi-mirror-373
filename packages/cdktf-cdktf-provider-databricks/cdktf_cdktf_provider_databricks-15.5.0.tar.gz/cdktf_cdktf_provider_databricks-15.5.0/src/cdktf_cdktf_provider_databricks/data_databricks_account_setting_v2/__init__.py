r'''
# `data_databricks_account_setting_v2`

Refer to the Terraform Registry for docs: [`data_databricks_account_setting_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2).
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


class DataDatabricksAccountSettingV2(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2 databricks_account_setting_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union["DataDatabricksAccountSettingV2BooleanVal", typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["DataDatabricksAccountSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["DataDatabricksAccountSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["DataDatabricksAccountSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksAccountSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["DataDatabricksAccountSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2 databricks_account_setting_v2} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#automatic_cluster_update_workspace DataDatabricksAccountSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#boolean_val DataDatabricksAccountSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#default_data_security_mode DataDatabricksAccountSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksAccountSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_default_data_security_mode DataDatabricksAccountSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_personal_compute DataDatabricksAccountSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_restrict_workspace_admins DataDatabricksAccountSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#integer_val DataDatabricksAccountSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#name DataDatabricksAccountSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#personal_compute DataDatabricksAccountSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restrict_workspace_admins DataDatabricksAccountSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#string_val DataDatabricksAccountSettingV2#string_val}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b006e7ced95e32286d2d37d6c41d48b5048f3de6944cf3017d3da8910d4bf0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAccountSettingV2Config(
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
        '''Generates CDKTF code for importing a DataDatabricksAccountSettingV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAccountSettingV2 to import.
        :param import_from_id: The id of the existing DataDatabricksAccountSettingV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAccountSettingV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50661141fcdfdfedfd8842eb6d685cff7d29d5e08e85407176b320c317222386)
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
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.
        '''
        value = DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.
        '''
        value = DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putAutomaticClusterUpdateWorkspace")
    def put_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.
        '''
        value = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace(
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
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        value_ = DataDatabricksAccountSettingV2BooleanVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putBooleanVal", [value_]))

    @jsii.member(jsii_name="putDefaultDataSecurityMode")
    def put_default_data_security_mode(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        value = DataDatabricksAccountSettingV2DefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectiveAibiDashboardEmbeddingAccessPolicy")
    def put_effective_aibi_dashboard_embedding_access_policy(
        self,
        *,
        access_policy_type: builtins.str,
    ) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putEffectiveAutomaticClusterUpdateWorkspace")
    def put_effective_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(
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
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode(
            status=status
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectivePersonalCompute")
    def put_effective_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        value_ = DataDatabricksAccountSettingV2EffectivePersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putEffectivePersonalCompute", [value_]))

    @jsii.member(jsii_name="putEffectiveRestrictWorkspaceAdmins")
    def put_effective_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins(
            status=status
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putIntegerVal")
    def put_integer_val(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        value_ = DataDatabricksAccountSettingV2IntegerVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putIntegerVal", [value_]))

    @jsii.member(jsii_name="putPersonalCompute")
    def put_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        value_ = DataDatabricksAccountSettingV2PersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putPersonalCompute", [value_]))

    @jsii.member(jsii_name="putRestrictWorkspaceAdmins")
    def put_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        value = DataDatabricksAccountSettingV2RestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putStringVal")
    def put_string_val(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        value_ = DataDatabricksAccountSettingV2StringVal(value=value)

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
    ) -> "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "aibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomains")
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "aibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspace")
    def automatic_cluster_update_workspace(
        self,
    ) -> "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "automaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="booleanVal")
    def boolean_val(self) -> "DataDatabricksAccountSettingV2BooleanValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2BooleanValOutputReference", jsii.get(self, "booleanVal"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityMode")
    def default_data_security_mode(
        self,
    ) -> "DataDatabricksAccountSettingV2DefaultDataSecurityModeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2DefaultDataSecurityModeOutputReference", jsii.get(self, "defaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicy")
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomains")
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspace")
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "effectiveAutomaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="effectiveBooleanVal")
    def effective_boolean_val(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveBooleanValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveBooleanValOutputReference", jsii.get(self, "effectiveBooleanVal"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityMode")
    def effective_default_data_security_mode(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityModeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityModeOutputReference", jsii.get(self, "effectiveDefaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveIntegerVal")
    def effective_integer_val(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveIntegerValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveIntegerValOutputReference", jsii.get(self, "effectiveIntegerVal"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalCompute")
    def effective_personal_compute(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectivePersonalComputeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectivePersonalComputeOutputReference", jsii.get(self, "effectivePersonalCompute"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdmins")
    def effective_restrict_workspace_admins(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference", jsii.get(self, "effectiveRestrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="effectiveStringVal")
    def effective_string_val(
        self,
    ) -> "DataDatabricksAccountSettingV2EffectiveStringValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveStringValOutputReference", jsii.get(self, "effectiveStringVal"))

    @builtins.property
    @jsii.member(jsii_name="integerVal")
    def integer_val(self) -> "DataDatabricksAccountSettingV2IntegerValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2IntegerValOutputReference", jsii.get(self, "integerVal"))

    @builtins.property
    @jsii.member(jsii_name="personalCompute")
    def personal_compute(
        self,
    ) -> "DataDatabricksAccountSettingV2PersonalComputeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2PersonalComputeOutputReference", jsii.get(self, "personalCompute"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdmins")
    def restrict_workspace_admins(
        self,
    ) -> "DataDatabricksAccountSettingV2RestrictWorkspaceAdminsOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2RestrictWorkspaceAdminsOutputReference", jsii.get(self, "restrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="stringVal")
    def string_val(self) -> "DataDatabricksAccountSettingV2StringValOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2StringValOutputReference", jsii.get(self, "stringVal"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicyInput")
    def aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "aibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomainsInput")
    def aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "aibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspaceInput")
    def automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace"]], jsii.get(self, "automaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="booleanValInput")
    def boolean_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2BooleanVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2BooleanVal"]], jsii.get(self, "booleanValInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityModeInput")
    def default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2DefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2DefaultDataSecurityMode"]], jsii.get(self, "defaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicyInput")
    def effective_aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomainsInput")
    def effective_aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspaceInput")
    def effective_automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]], jsii.get(self, "effectiveAutomaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityModeInput")
    def effective_default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode"]], jsii.get(self, "effectiveDefaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalComputeInput")
    def effective_personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectivePersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectivePersonalCompute"]], jsii.get(self, "effectivePersonalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdminsInput")
    def effective_restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins"]], jsii.get(self, "effectiveRestrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="integerValInput")
    def integer_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2IntegerVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2IntegerVal"]], jsii.get(self, "integerValInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="personalComputeInput")
    def personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2PersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2PersonalCompute"]], jsii.get(self, "personalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdminsInput")
    def restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2RestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2RestrictWorkspaceAdmins"]], jsii.get(self, "restrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="stringValInput")
    def string_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2StringVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2StringVal"]], jsii.get(self, "stringValInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c440ddc5c87f780d675124c5ba449956faac69b0b948f24affac62e5187684c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a158eb9b5c1407123f17b22dd5a6bbf1c9a77c766e96489330c0caea0ec64d3a)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb4caddd5b939ed2c8c839f88c3a34550aea857a3643740451579a2320e9336e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c22b0754908c6f29812db058275cbff8991b9f13c8023ee9b60995172719747e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350cb578b81c09084a54d2dd08ee6bafbc8bab37c7b2fc3eea80bfb74c52804b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574e336d697042612ecd80792d41dcaee6ee76b9e466114626b1c55d5f7eb747)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e1e49700e780b73065bcfe0603a339d35a4bca1065185acd1c68405fa801b32)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddf965c17dd91e11e9ce01a2ad519c1c48946fb8a1482060ecbb2c0cf39bf920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cb62427bfa47c318800a4457af4479ffc7d20e112e79c4ea48e23a9d54e4761)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6d27b686770eaebcbbf207fd4693cf966653987f569147038e95f594619fde1)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a184334a29e3e4a89b416cb06021046ff73804288afc5d1afb5758ac38e77426)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca223d589a42c326fa1d58478b0a20d0cf04f310494ec5e05bcc7f4c2f8546ca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ccb3f67e5db40fad40d7aa7264cee27b15c2f5dbf908144a8fb7c7a642016228)
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
            type_hints = typing.get_type_hints(_typecheckingstub__931b2afc64581d88c3aaf8a5ec19d7f09bbcea8ed1d4d642cf41f8295636d4cb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90e2c9655789c6657e65feea5728cf3404d7faa927837fd8587b45db738da437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd8643953066098762bb90ec8e7e857f5f5139524cd598ee05bb3f89700b17a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57280abe5f6ed95769991a50a8fbfca97fae515def3493d68f06578ed7920d02)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a4727fa8a2d8ef63438c3953a6de41062b3b1fc8806e6c4d0f138bf5af9ece6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.
        '''
        value = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5491b846ce925dcb4957b7e93b849b072c09964b1ad613b42c6ee6579def617c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ed43a541c494f0648a340dc60f3fc1bdd7c46b5dad4bdc7bba73ed85da4c647)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcb52c98f8d139a6937c09d294a358fe8467293dc3b2673211f4492bc2136e3f)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.
        '''
        value = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9a5c81d30a67cc18a741cfeea0077f0b2fccbb6ff228f632b95d755a15c7cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36258d2ef724ed75928c3c9d0edc4503a78d720165e25c5ba876b4678b9ebccf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6471bac0f349928dd1cca97709cf5b5af7a06d3cf06968c4439f1eabb91c972f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8700a7d51ebf46baeeec54db30c23918e394114e1e404394a2683caf1f3326)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d24c0085f6b1a720b12f10f48108c4a7d9f9ae2a37672e1745e35d18d35db2ab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__50dcab246e30a0fefe74bb717024cedea0e7b4ea4cdee20127767a6c71efe4d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__519bcb279e810c9fc5c1d3e22356e8fbbff58d3eee2f3ed36d2854d84c9e41b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deda47f022ac1cc0722003d43237c4079d1039ca432a0438cb4062284f2b8944)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5664966e0aaa44574a3caacb85cc5d9be2984757a2edad779ca5818f9702c3f6)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.
        '''
        value = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f316f1015bed184e3fa4ce47096c404e690e13d86aa4b940c9a845eb9fb0be45)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd6719171262ad25f2047bac091ba71395f363d31b2e8f99383a62a1b04d0cca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__03a8e2196f0399f13481869989cecabf22beebfc7776d79d13ec8415920e7163)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abb12169ca8ebf4e5435efe3c18ed232a499cce241729e655a86e2940af35039)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2BooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2BooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f0131842f13e0ed855c893e89a4e11e14f4760e134fc14aaa82174d29ea31e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2BooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2BooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2BooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__785610a399cce477ff87c508fd22d66e1c01b5f9e4b527bc13e2bca076eed40b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9514548cc8684ec51a162b6838d457c16800d557d9e01f6d4f05dd6f8c45f381)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2BooleanVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2BooleanVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2BooleanVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b85c2d5e63c3fbe5cc45609f932ca90a5aadf285248ace9b20be837f1f1a875f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2Config",
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
class DataDatabricksAccountSettingV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["DataDatabricksAccountSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["DataDatabricksAccountSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["DataDatabricksAccountSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksAccountSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["DataDatabricksAccountSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#automatic_cluster_update_workspace DataDatabricksAccountSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#boolean_val DataDatabricksAccountSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#default_data_security_mode DataDatabricksAccountSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksAccountSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_default_data_security_mode DataDatabricksAccountSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_personal_compute DataDatabricksAccountSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_restrict_workspace_admins DataDatabricksAccountSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#integer_val DataDatabricksAccountSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#name DataDatabricksAccountSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#personal_compute DataDatabricksAccountSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restrict_workspace_admins DataDatabricksAccountSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#string_val DataDatabricksAccountSettingV2#string_val}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aibi_dashboard_embedding_access_policy, dict):
            aibi_dashboard_embedding_access_policy = DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy(**aibi_dashboard_embedding_access_policy)
        if isinstance(aibi_dashboard_embedding_approved_domains, dict):
            aibi_dashboard_embedding_approved_domains = DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains(**aibi_dashboard_embedding_approved_domains)
        if isinstance(automatic_cluster_update_workspace, dict):
            automatic_cluster_update_workspace = DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace(**automatic_cluster_update_workspace)
        if isinstance(boolean_val, dict):
            boolean_val = DataDatabricksAccountSettingV2BooleanVal(**boolean_val)
        if isinstance(default_data_security_mode, dict):
            default_data_security_mode = DataDatabricksAccountSettingV2DefaultDataSecurityMode(**default_data_security_mode)
        if isinstance(effective_aibi_dashboard_embedding_access_policy, dict):
            effective_aibi_dashboard_embedding_access_policy = DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(**effective_aibi_dashboard_embedding_access_policy)
        if isinstance(effective_aibi_dashboard_embedding_approved_domains, dict):
            effective_aibi_dashboard_embedding_approved_domains = DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(**effective_aibi_dashboard_embedding_approved_domains)
        if isinstance(effective_automatic_cluster_update_workspace, dict):
            effective_automatic_cluster_update_workspace = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(**effective_automatic_cluster_update_workspace)
        if isinstance(effective_default_data_security_mode, dict):
            effective_default_data_security_mode = DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode(**effective_default_data_security_mode)
        if isinstance(effective_personal_compute, dict):
            effective_personal_compute = DataDatabricksAccountSettingV2EffectivePersonalCompute(**effective_personal_compute)
        if isinstance(effective_restrict_workspace_admins, dict):
            effective_restrict_workspace_admins = DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins(**effective_restrict_workspace_admins)
        if isinstance(integer_val, dict):
            integer_val = DataDatabricksAccountSettingV2IntegerVal(**integer_val)
        if isinstance(personal_compute, dict):
            personal_compute = DataDatabricksAccountSettingV2PersonalCompute(**personal_compute)
        if isinstance(restrict_workspace_admins, dict):
            restrict_workspace_admins = DataDatabricksAccountSettingV2RestrictWorkspaceAdmins(**restrict_workspace_admins)
        if isinstance(string_val, dict):
            string_val = DataDatabricksAccountSettingV2StringVal(**string_val)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__353f082ce0550fdb1494f7267d92e2511383a6128d4031789a26a3e2586259fd)
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
    ) -> typing.Optional[DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy], result)

    @builtins.property
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional[DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains], result)

    @builtins.property
    def automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#automatic_cluster_update_workspace DataDatabricksAccountSettingV2#automatic_cluster_update_workspace}.'''
        result = self._values.get("automatic_cluster_update_workspace")
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace], result)

    @builtins.property
    def boolean_val(self) -> typing.Optional[DataDatabricksAccountSettingV2BooleanVal]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#boolean_val DataDatabricksAccountSettingV2#boolean_val}.'''
        result = self._values.get("boolean_val")
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2BooleanVal], result)

    @builtins.property
    def default_data_security_mode(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2DefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#default_data_security_mode DataDatabricksAccountSettingV2#default_data_security_mode}.'''
        result = self._values.get("default_data_security_mode")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2DefaultDataSecurityMode"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksAccountSettingV2#effective_aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"], result)

    @builtins.property
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksAccountSettingV2#effective_automatic_cluster_update_workspace}.'''
        result = self._values.get("effective_automatic_cluster_update_workspace")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace"], result)

    @builtins.property
    def effective_default_data_security_mode(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_default_data_security_mode DataDatabricksAccountSettingV2#effective_default_data_security_mode}.'''
        result = self._values.get("effective_default_data_security_mode")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode"], result)

    @builtins.property
    def effective_personal_compute(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectivePersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_personal_compute DataDatabricksAccountSettingV2#effective_personal_compute}.'''
        result = self._values.get("effective_personal_compute")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectivePersonalCompute"], result)

    @builtins.property
    def effective_restrict_workspace_admins(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#effective_restrict_workspace_admins DataDatabricksAccountSettingV2#effective_restrict_workspace_admins}.'''
        result = self._values.get("effective_restrict_workspace_admins")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins"], result)

    @builtins.property
    def integer_val(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2IntegerVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#integer_val DataDatabricksAccountSettingV2#integer_val}.'''
        result = self._values.get("integer_val")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2IntegerVal"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#name DataDatabricksAccountSettingV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personal_compute(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2PersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#personal_compute DataDatabricksAccountSettingV2#personal_compute}.'''
        result = self._values.get("personal_compute")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2PersonalCompute"], result)

    @builtins.property
    def restrict_workspace_admins(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2RestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restrict_workspace_admins DataDatabricksAccountSettingV2#restrict_workspace_admins}.'''
        result = self._values.get("restrict_workspace_admins")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2RestrictWorkspaceAdmins"], result)

    @builtins.property
    def string_val(self) -> typing.Optional["DataDatabricksAccountSettingV2StringVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#string_val DataDatabricksAccountSettingV2#string_val}.'''
        result = self._values.get("string_val")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2StringVal"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2DefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksAccountSettingV2DefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1327d5d79a60d60338c72e42b18da36851ad3c5931bd7816a13a5060877a19b9)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2DefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2DefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2DefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4535b2501b15d49a9a5ded3887650561e2e7a1cccc99eaf01749cc62dcd5907)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ec10f83188555476f0debc2c5e2daea71ecc91b15e2b9554fdcd6dd9d57c4a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2DefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2DefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2DefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f72fe93ed218feb5d1a5e8ef2d8e6f6b1e5c03a1fda1a11bf0d4ee940b7076ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18c53ce7412ea6b8b7b3ef3f92a6287d64a6c5ddf3348798d64690b84c7f37b5)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#access_policy_type DataDatabricksAccountSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0cc8c0f69bfc30b90a8a83d597dd71f1cad61f1df6a41f1897b5ffa6e9451e8d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2406aa5bccf0faeaf925f65467c35c2c977a979f4c9ece49e8c30b8a5c959316)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47cf05f0b59971af19730e617f41aaa27da298710280632a692adb146082855f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e34c51b23480b91aafd5dd0f2f00542fb25967a89e0064f3fa9ea6462922524)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#approved_domains DataDatabricksAccountSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8cf657d89d672d6a1cf324016e3e53ff655ac60ad3bb870e81551d639a9132a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__11d05da1d8d0caa3fd4d93942c53cb35b3d7b45150d91ee68a260415024e47e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c4d23d40c66ddb8fa9ddf6f35ab3f6c603d4063433e9ca61ce8385c562717b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e74d76ce41aa84ef5507dff9be7ab25489b52014cda3c77053245265da60c702)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#can_toggle DataDatabricksAccountSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enabled DataDatabricksAccountSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#enablement_details DataDatabricksAccountSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#maintenance_window DataDatabricksAccountSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#restart_even_if_no_updates_available DataDatabricksAccountSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca67a120e9bc27707a1db90ea9233d4d20f2b2409e8d789f439f479cda1beac)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fdec7c4de198a1a5e960f2f2dab192e96a208ae9d453b6689de39321ff39cf3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__79afb52a531bc322979c0c7956f67eac19acc0491de1421d7156feea881a5406)
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
            type_hints = typing.get_type_hints(_typecheckingstub__007d90387d68e6ebc19f091f79b57eaebd5a0ca86afa1174505bc8e395d84904)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dce7fe7dd8c4631b4da2152fe8ab471173e4bb5f5dba88d9e88051958359f4d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f778b6546efb38a1619d714a95a47122f617ead22d3e3b0f500a0b1d189e223d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506556d21d9227bd13e15581a9db2f9ad22c523ec22ec53073a13f4a1161d636)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb46ab55bb6e8b6404ac0a89f8e94746e6d2cb43d94cc6920a4cd9b308a5204b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11678e3af8275d7482f15d28aa630249bfbe5d8115a2083d671f38e6b7ee1cdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2034103b424cdafecdb134196d2da3d5edb23ebe0b9728120cff3083c68ec61f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#day_of_week DataDatabricksAccountSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#frequency DataDatabricksAccountSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#window_start_time DataDatabricksAccountSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58b6a7a30fe4169dd8c42d93aa4130d826d6e767c805098da8a7d2d6abcbe74c)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee9065a5e5dc06c6d14dcbf1c365b9f881a8e26e6bd9fe2c8b1343d5e142c3e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5fc94a4b31fb9d129503cb1f889db37b6d23eaa574f3d3ef04fd49d2e4ec741)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ceb91fe938daae0cda46cb66f337a3151a6fc59f93de7a3e09bbcc4d1641572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6172371e2b6fbf5278f7eb18a07ed94d9ba908427afa36235d20cceb75c73e11)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#hours DataDatabricksAccountSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#minutes DataDatabricksAccountSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d33aa25e33f1829e80ec77c852a7aef6be1957e9fdc3c5767581bcfdf37d19ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f4e6e42f6d183573fe14b84eca1686fac5d49d715563d55e4986c65b6f0d8e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99badb1262e76a156bf1b0aeb7134875ba8d24d857dd7a4f021875b36639fc56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94fa6c763013eef5d7b9a18649203440ed5e48e65c183dfedc02d02d7cee375)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9dd531fad4a509153bedaaee07a1a3f937fae93b1cc6fa5e1b67d884994843b)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#forced_for_compliance_mode DataDatabricksAccountSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_disabled_entitlement DataDatabricksAccountSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksAccountSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#week_day_based_schedule DataDatabricksAccountSettingV2#week_day_based_schedule}.
        '''
        value = DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__7025c99e7077f33476214fd5f73e0d5e03b9cd6a41513def6bc3c855d542f82d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4054156f9434f4e1e99d09f652eb385ceac5355c50fc24835f8c3579ec7eaca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a69200b7b1b999983f5812ebfa55b47d24e43ca1cd3e5131e90ad4176e6e313)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52afb5588fddb7d6b7561dba9a3307fb36093d59ef227cd095ae633f5588acbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveBooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2EffectiveBooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b970ff38d22962d5dcaa9c5216bb3e258e51387085247938fd40671597850bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveBooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveBooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveBooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cb8c4475315ece23749d0cb754631a536a60a6675d02841d516e5e2427db574)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aeb62e82015ecbb91764ee18aae45f308a6f260d2ca2a6430c59ad3ba2fab45c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAccountSettingV2EffectiveBooleanVal]:
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2EffectiveBooleanVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAccountSettingV2EffectiveBooleanVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaa7e9185b883df649301c39dc2ec73e581def1a90fa02387027f488872c705c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68bdae60c4693dd2bd2fee0325d7f2e3e00a152eee1d8aaf564641a8cc4df0d5)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f256f963969638db3d0842cbdf07703e73b83a4f928eb43b5f7be90766980a66)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b18a10291300b32b2723609cf2d57cf1ed617c353804c8eb84f1f03112561ee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc8fcd687c7a1485daeadb07c0478cec7351dcca0a7ce7f679905884cbe20d88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveIntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2EffectiveIntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebd9d1afa177e5c802d0b773fd0a22f658407ca7aa459faeb63d80132f1f4f36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveIntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveIntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveIntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e12fa4039daf05e20ce8a569384dbbd1c57a3e55cd0f4d81b42dffbeeaff2af5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__368dd3753aeba94a093b9715220ab0d8af32a93cb41e131b529e2a5b9fc772be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAccountSettingV2EffectiveIntegerVal]:
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2EffectiveIntegerVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAccountSettingV2EffectiveIntegerVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__213abaaed6fffe2f6acf43dbb68cc49270b5df33db79469c862c17b404a4cdb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectivePersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2EffectivePersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90b5c0b0ae222c9e0198d5804917c27ff736d206ae2d8af7153308d694ba17d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectivePersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectivePersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectivePersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b987fd1a198ecca9c22f0a4cb96cb565bd49ac14b89a3f9154ee120fd42b02a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8341ca81bf7d75953bff0904380bc408cd70e2c0553a727bda9f52deee939b9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectivePersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectivePersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectivePersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27bdd967a38559742f8b3cb6b816915fcf6ba4080a792600e47c627d553bfd90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d61e8a788497905eeade4734bc5cc1046ecfeb0cd3a0e53b77b18569d1c1543c)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2311790d4bb5b0e3e1ce89faef2279003b6a56001d9f0f8e60e46ea8177fface)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d13390c50e9c0b7ddd3b125d9f496e50ac273238c7b9bcb4e9e8837e6aeafaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68d1c659c988f2ceb9c7dc51ac8fe4bde3ae693281884a076ae7916ddee81f31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveStringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2EffectiveStringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ad1536104c521a4ef7b41ed5e2c2c7a5407a9808a46b321358a4cc4f2fbe4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2EffectiveStringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2EffectiveStringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2EffectiveStringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b73555ebc17541b001f53c4460e955f50f556d2810291d1674adc89553c5ceb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__30f36de40fd4cc6afc03fdec44333c5a4d4433f30dd1778262293119438d47a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksAccountSettingV2EffectiveStringVal]:
        return typing.cast(typing.Optional[DataDatabricksAccountSettingV2EffectiveStringVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksAccountSettingV2EffectiveStringVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e5809973f2648bcdd05604fb309f387ab32159f5f0abefa07d97add3a5f5d3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2IntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2IntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c787f1655d3b49f72e1b80bd0f3a6b9b5625cfb87c94b84825ffb9dc03abbcbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2IntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2IntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2IntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5beb5bb0d619d48f95e3c8ba2b1fe13329dce91e208b5966b251cfdfbe4a712f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90ba251aff24ecf5ca0750d517cc3c00dacdcc3b9fd8af6271cbe23aeaf2084b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2IntegerVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2IntegerVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2IntegerVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__316415eabb372e6822a4f995af07d46ea8d248e84a23f05f0ac81bc5a47ec4b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2PersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2PersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a6b5118f093d7b90044731fde554e52450fa36bf9d9ea90ccb333ef3cb61fe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2PersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2PersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2PersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70d8ba4b583bd9634eab4ee6f5017f278308c200fa601ca9bedb4d8d8b6c0be6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48f012649aedbc27919e09666152ac858174a8e0b268392fe0da6560efcd8fd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2PersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2PersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2PersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a9f18f834c6f688e13bed76a9613e9c6b0bd5f4469c524d38444b2ccc7df22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2RestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksAccountSettingV2RestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38388a5c8fcd3bae5d10edfd87039dd2c106b7accc83d7dfd617f0bf1748d8f2)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#status DataDatabricksAccountSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2RestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2RestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2RestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4f5a7165feeee055d92b0dd9988d4be0775a9b979410e93d626edf813f1691f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58f2c23d4f173cbc7c362967e08d2f4b6c7a1776a77e5f54d92876be3cd97573)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2RestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2RestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2RestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__728eca717a58c2257bbf2afb694101158753e3f52ee6d8a8c7d1af9eada69153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2StringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksAccountSettingV2StringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aefa710391aa5a0638fa009e97c5342c7a5fb5648d4e4a148fb0bf9ddfa4dc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/account_setting_v2#value DataDatabricksAccountSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAccountSettingV2StringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAccountSettingV2StringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAccountSettingV2.DataDatabricksAccountSettingV2StringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b27812f5a82b8e7a8be8e2b97fe00cc39d42da5cccd16759ce7d41e61c6da6b1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18d03f4cfb479874b5bdb8ae1b63a842ec2f392b2754030da2365c2fec082f75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2StringVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2StringVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2StringVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f4b97efb8c4f131a65b7b651008d76d263bae365d0c60cd4ec4b4952d1cd644)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAccountSettingV2",
    "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy",
    "DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
    "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains",
    "DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
    "DataDatabricksAccountSettingV2BooleanVal",
    "DataDatabricksAccountSettingV2BooleanValOutputReference",
    "DataDatabricksAccountSettingV2Config",
    "DataDatabricksAccountSettingV2DefaultDataSecurityMode",
    "DataDatabricksAccountSettingV2DefaultDataSecurityModeOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    "DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
    "DataDatabricksAccountSettingV2EffectiveBooleanVal",
    "DataDatabricksAccountSettingV2EffectiveBooleanValOutputReference",
    "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode",
    "DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityModeOutputReference",
    "DataDatabricksAccountSettingV2EffectiveIntegerVal",
    "DataDatabricksAccountSettingV2EffectiveIntegerValOutputReference",
    "DataDatabricksAccountSettingV2EffectivePersonalCompute",
    "DataDatabricksAccountSettingV2EffectivePersonalComputeOutputReference",
    "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins",
    "DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
    "DataDatabricksAccountSettingV2EffectiveStringVal",
    "DataDatabricksAccountSettingV2EffectiveStringValOutputReference",
    "DataDatabricksAccountSettingV2IntegerVal",
    "DataDatabricksAccountSettingV2IntegerValOutputReference",
    "DataDatabricksAccountSettingV2PersonalCompute",
    "DataDatabricksAccountSettingV2PersonalComputeOutputReference",
    "DataDatabricksAccountSettingV2RestrictWorkspaceAdmins",
    "DataDatabricksAccountSettingV2RestrictWorkspaceAdminsOutputReference",
    "DataDatabricksAccountSettingV2StringVal",
    "DataDatabricksAccountSettingV2StringValOutputReference",
]

publication.publish()

def _typecheckingstub__22b006e7ced95e32286d2d37d6c41d48b5048f3de6944cf3017d3da8910d4bf0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[DataDatabricksAccountSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[DataDatabricksAccountSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksAccountSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__50661141fcdfdfedfd8842eb6d685cff7d29d5e08e85407176b320c317222386(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c440ddc5c87f780d675124c5ba449956faac69b0b948f24affac62e5187684c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a158eb9b5c1407123f17b22dd5a6bbf1c9a77c766e96489330c0caea0ec64d3a(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb4caddd5b939ed2c8c839f88c3a34550aea857a3643740451579a2320e9336e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c22b0754908c6f29812db058275cbff8991b9f13c8023ee9b60995172719747e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350cb578b81c09084a54d2dd08ee6bafbc8bab37c7b2fc3eea80bfb74c52804b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574e336d697042612ecd80792d41dcaee6ee76b9e466114626b1c55d5f7eb747(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e1e49700e780b73065bcfe0603a339d35a4bca1065185acd1c68405fa801b32(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddf965c17dd91e11e9ce01a2ad519c1c48946fb8a1482060ecbb2c0cf39bf920(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cb62427bfa47c318800a4457af4479ffc7d20e112e79c4ea48e23a9d54e4761(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d27b686770eaebcbbf207fd4693cf966653987f569147038e95f594619fde1(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a184334a29e3e4a89b416cb06021046ff73804288afc5d1afb5758ac38e77426(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca223d589a42c326fa1d58478b0a20d0cf04f310494ec5e05bcc7f4c2f8546ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccb3f67e5db40fad40d7aa7264cee27b15c2f5dbf908144a8fb7c7a642016228(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__931b2afc64581d88c3aaf8a5ec19d7f09bbcea8ed1d4d642cf41f8295636d4cb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90e2c9655789c6657e65feea5728cf3404d7faa927837fd8587b45db738da437(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd8643953066098762bb90ec8e7e857f5f5139524cd598ee05bb3f89700b17a4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57280abe5f6ed95769991a50a8fbfca97fae515def3493d68f06578ed7920d02(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4727fa8a2d8ef63438c3953a6de41062b3b1fc8806e6c4d0f138bf5af9ece6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5491b846ce925dcb4957b7e93b849b072c09964b1ad613b42c6ee6579def617c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ed43a541c494f0648a340dc60f3fc1bdd7c46b5dad4bdc7bba73ed85da4c647(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb52c98f8d139a6937c09d294a358fe8467293dc3b2673211f4492bc2136e3f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9a5c81d30a67cc18a741cfeea0077f0b2fccbb6ff228f632b95d755a15c7cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36258d2ef724ed75928c3c9d0edc4503a78d720165e25c5ba876b4678b9ebccf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6471bac0f349928dd1cca97709cf5b5af7a06d3cf06968c4439f1eabb91c972f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8700a7d51ebf46baeeec54db30c23918e394114e1e404394a2683caf1f3326(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d24c0085f6b1a720b12f10f48108c4a7d9f9ae2a37672e1745e35d18d35db2ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50dcab246e30a0fefe74bb717024cedea0e7b4ea4cdee20127767a6c71efe4d7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__519bcb279e810c9fc5c1d3e22356e8fbbff58d3eee2f3ed36d2854d84c9e41b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deda47f022ac1cc0722003d43237c4079d1039ca432a0438cb4062284f2b8944(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5664966e0aaa44574a3caacb85cc5d9be2984757a2edad779ca5818f9702c3f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f316f1015bed184e3fa4ce47096c404e690e13d86aa4b940c9a845eb9fb0be45(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd6719171262ad25f2047bac091ba71395f363d31b2e8f99383a62a1b04d0cca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03a8e2196f0399f13481869989cecabf22beebfc7776d79d13ec8415920e7163(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abb12169ca8ebf4e5435efe3c18ed232a499cce241729e655a86e2940af35039(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f0131842f13e0ed855c893e89a4e11e14f4760e134fc14aaa82174d29ea31e0(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785610a399cce477ff87c508fd22d66e1c01b5f9e4b527bc13e2bca076eed40b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9514548cc8684ec51a162b6838d457c16800d557d9e01f6d4f05dd6f8c45f381(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b85c2d5e63c3fbe5cc45609f932ca90a5aadf285248ace9b20be837f1f1a875f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2BooleanVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__353f082ce0550fdb1494f7267d92e2511383a6128d4031789a26a3e2586259fd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksAccountSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[DataDatabricksAccountSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[DataDatabricksAccountSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksAccountSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[DataDatabricksAccountSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1327d5d79a60d60338c72e42b18da36851ad3c5931bd7816a13a5060877a19b9(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4535b2501b15d49a9a5ded3887650561e2e7a1cccc99eaf01749cc62dcd5907(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec10f83188555476f0debc2c5e2daea71ecc91b15e2b9554fdcd6dd9d57c4a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f72fe93ed218feb5d1a5e8ef2d8e6f6b1e5c03a1fda1a11bf0d4ee940b7076ec(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2DefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18c53ce7412ea6b8b7b3ef3f92a6287d64a6c5ddf3348798d64690b84c7f37b5(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc8c0f69bfc30b90a8a83d597dd71f1cad61f1df6a41f1897b5ffa6e9451e8d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2406aa5bccf0faeaf925f65467c35c2c977a979f4c9ece49e8c30b8a5c959316(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47cf05f0b59971af19730e617f41aaa27da298710280632a692adb146082855f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e34c51b23480b91aafd5dd0f2f00542fb25967a89e0064f3fa9ea6462922524(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8cf657d89d672d6a1cf324016e3e53ff655ac60ad3bb870e81551d639a9132a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11d05da1d8d0caa3fd4d93942c53cb35b3d7b45150d91ee68a260415024e47e5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c4d23d40c66ddb8fa9ddf6f35ab3f6c603d4063433e9ca61ce8385c562717b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e74d76ce41aa84ef5507dff9be7ab25489b52014cda3c77053245265da60c702(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca67a120e9bc27707a1db90ea9233d4d20f2b2409e8d789f439f479cda1beac(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fdec7c4de198a1a5e960f2f2dab192e96a208ae9d453b6689de39321ff39cf3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79afb52a531bc322979c0c7956f67eac19acc0491de1421d7156feea881a5406(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__007d90387d68e6ebc19f091f79b57eaebd5a0ca86afa1174505bc8e395d84904(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce7fe7dd8c4631b4da2152fe8ab471173e4bb5f5dba88d9e88051958359f4d3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f778b6546efb38a1619d714a95a47122f617ead22d3e3b0f500a0b1d189e223d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506556d21d9227bd13e15581a9db2f9ad22c523ec22ec53073a13f4a1161d636(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb46ab55bb6e8b6404ac0a89f8e94746e6d2cb43d94cc6920a4cd9b308a5204b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11678e3af8275d7482f15d28aa630249bfbe5d8115a2083d671f38e6b7ee1cdd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2034103b424cdafecdb134196d2da3d5edb23ebe0b9728120cff3083c68ec61f(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b6a7a30fe4169dd8c42d93aa4130d826d6e767c805098da8a7d2d6abcbe74c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9065a5e5dc06c6d14dcbf1c365b9f881a8e26e6bd9fe2c8b1343d5e142c3e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5fc94a4b31fb9d129503cb1f889db37b6d23eaa574f3d3ef04fd49d2e4ec741(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ceb91fe938daae0cda46cb66f337a3151a6fc59f93de7a3e09bbcc4d1641572(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6172371e2b6fbf5278f7eb18a07ed94d9ba908427afa36235d20cceb75c73e11(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d33aa25e33f1829e80ec77c852a7aef6be1957e9fdc3c5767581bcfdf37d19ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f4e6e42f6d183573fe14b84eca1686fac5d49d715563d55e4986c65b6f0d8e8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99badb1262e76a156bf1b0aeb7134875ba8d24d857dd7a4f021875b36639fc56(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94fa6c763013eef5d7b9a18649203440ed5e48e65c183dfedc02d02d7cee375(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9dd531fad4a509153bedaaee07a1a3f937fae93b1cc6fa5e1b67d884994843b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7025c99e7077f33476214fd5f73e0d5e03b9cd6a41513def6bc3c855d542f82d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4054156f9434f4e1e99d09f652eb385ceac5355c50fc24835f8c3579ec7eaca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a69200b7b1b999983f5812ebfa55b47d24e43ca1cd3e5131e90ad4176e6e313(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52afb5588fddb7d6b7561dba9a3307fb36093d59ef227cd095ae633f5588acbb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b970ff38d22962d5dcaa9c5216bb3e258e51387085247938fd40671597850bef(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb8c4475315ece23749d0cb754631a536a60a6675d02841d516e5e2427db574(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb62e82015ecbb91764ee18aae45f308a6f260d2ca2a6430c59ad3ba2fab45c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaa7e9185b883df649301c39dc2ec73e581def1a90fa02387027f488872c705c(
    value: typing.Optional[DataDatabricksAccountSettingV2EffectiveBooleanVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68bdae60c4693dd2bd2fee0325d7f2e3e00a152eee1d8aaf564641a8cc4df0d5(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f256f963969638db3d0842cbdf07703e73b83a4f928eb43b5f7be90766980a66(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b18a10291300b32b2723609cf2d57cf1ed617c353804c8eb84f1f03112561ee2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc8fcd687c7a1485daeadb07c0478cec7351dcca0a7ce7f679905884cbe20d88(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveDefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebd9d1afa177e5c802d0b773fd0a22f658407ca7aa459faeb63d80132f1f4f36(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e12fa4039daf05e20ce8a569384dbbd1c57a3e55cd0f4d81b42dffbeeaff2af5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__368dd3753aeba94a093b9715220ab0d8af32a93cb41e131b529e2a5b9fc772be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__213abaaed6fffe2f6acf43dbb68cc49270b5df33db79469c862c17b404a4cdb9(
    value: typing.Optional[DataDatabricksAccountSettingV2EffectiveIntegerVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90b5c0b0ae222c9e0198d5804917c27ff736d206ae2d8af7153308d694ba17d3(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b987fd1a198ecca9c22f0a4cb96cb565bd49ac14b89a3f9154ee120fd42b02a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8341ca81bf7d75953bff0904380bc408cd70e2c0553a727bda9f52deee939b9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27bdd967a38559742f8b3cb6b816915fcf6ba4080a792600e47c627d553bfd90(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectivePersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d61e8a788497905eeade4734bc5cc1046ecfeb0cd3a0e53b77b18569d1c1543c(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2311790d4bb5b0e3e1ce89faef2279003b6a56001d9f0f8e60e46ea8177fface(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d13390c50e9c0b7ddd3b125d9f496e50ac273238c7b9bcb4e9e8837e6aeafaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68d1c659c988f2ceb9c7dc51ac8fe4bde3ae693281884a076ae7916ddee81f31(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2EffectiveRestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ad1536104c521a4ef7b41ed5e2c2c7a5407a9808a46b321358a4cc4f2fbe4a(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b73555ebc17541b001f53c4460e955f50f556d2810291d1674adc89553c5ceb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30f36de40fd4cc6afc03fdec44333c5a4d4433f30dd1778262293119438d47a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e5809973f2648bcdd05604fb309f387ab32159f5f0abefa07d97add3a5f5d3a(
    value: typing.Optional[DataDatabricksAccountSettingV2EffectiveStringVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c787f1655d3b49f72e1b80bd0f3a6b9b5625cfb87c94b84825ffb9dc03abbcbe(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5beb5bb0d619d48f95e3c8ba2b1fe13329dce91e208b5966b251cfdfbe4a712f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90ba251aff24ecf5ca0750d517cc3c00dacdcc3b9fd8af6271cbe23aeaf2084b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__316415eabb372e6822a4f995af07d46ea8d248e84a23f05f0ac81bc5a47ec4b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2IntegerVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a6b5118f093d7b90044731fde554e52450fa36bf9d9ea90ccb333ef3cb61fe4(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d8ba4b583bd9634eab4ee6f5017f278308c200fa601ca9bedb4d8d8b6c0be6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48f012649aedbc27919e09666152ac858174a8e0b268392fe0da6560efcd8fd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a9f18f834c6f688e13bed76a9613e9c6b0bd5f4469c524d38444b2ccc7df22(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2PersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38388a5c8fcd3bae5d10edfd87039dd2c106b7accc83d7dfd617f0bf1748d8f2(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f5a7165feeee055d92b0dd9988d4be0775a9b979410e93d626edf813f1691f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58f2c23d4f173cbc7c362967e08d2f4b6c7a1776a77e5f54d92876be3cd97573(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__728eca717a58c2257bbf2afb694101158753e3f52ee6d8a8c7d1af9eada69153(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2RestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aefa710391aa5a0638fa009e97c5342c7a5fb5648d4e4a148fb0bf9ddfa4dc4(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27812f5a82b8e7a8be8e2b97fe00cc39d42da5cccd16759ce7d41e61c6da6b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18d03f4cfb479874b5bdb8ae1b63a842ec2f392b2754030da2365c2fec082f75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f4b97efb8c4f131a65b7b651008d76d263bae365d0c60cd4ec4b4952d1cd644(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAccountSettingV2StringVal]],
) -> None:
    """Type checking stubs"""
    pass
