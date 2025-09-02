r'''
# `data_databricks_workspace_setting_v2`

Refer to the Terraform Registry for docs: [`data_databricks_workspace_setting_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2).
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


class DataDatabricksWorkspaceSettingV2(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2 databricks_workspace_setting_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2BooleanVal", typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2 databricks_workspace_setting_v2} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#boolean_val DataDatabricksWorkspaceSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#default_data_security_mode DataDatabricksWorkspaceSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_default_data_security_mode DataDatabricksWorkspaceSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_personal_compute DataDatabricksWorkspaceSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_restrict_workspace_admins DataDatabricksWorkspaceSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#integer_val DataDatabricksWorkspaceSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#name DataDatabricksWorkspaceSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#personal_compute DataDatabricksWorkspaceSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restrict_workspace_admins DataDatabricksWorkspaceSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#string_val DataDatabricksWorkspaceSettingV2#string_val}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#workspace_id DataDatabricksWorkspaceSettingV2#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a2bad695c9beaab56f98c083650ac90d0a53857e7b080801d8f176796eef96a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksWorkspaceSettingV2Config(
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
        '''Generates CDKTF code for importing a DataDatabricksWorkspaceSettingV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksWorkspaceSettingV2 to import.
        :param import_from_id: The id of the existing DataDatabricksWorkspaceSettingV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksWorkspaceSettingV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b0cfb6b27440205520c2c43f485b695b806c61141e3251e02a440152da852fb)
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
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.
        '''
        value = DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.
        '''
        value = DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putAutomaticClusterUpdateWorkspace")
    def put_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        value = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace(
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
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        value_ = DataDatabricksWorkspaceSettingV2BooleanVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putBooleanVal", [value_]))

    @jsii.member(jsii_name="putDefaultDataSecurityMode")
    def put_default_data_security_mode(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        value = DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectiveAibiDashboardEmbeddingAccessPolicy")
    def put_effective_aibi_dashboard_embedding_access_policy(
        self,
        *,
        access_policy_type: builtins.str,
    ) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putEffectiveAutomaticClusterUpdateWorkspace")
    def put_effective_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(
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
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode(
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
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        value_ = DataDatabricksWorkspaceSettingV2EffectivePersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putEffectivePersonalCompute", [value_]))

    @jsii.member(jsii_name="putEffectiveRestrictWorkspaceAdmins")
    def put_effective_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(
            status=status
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putIntegerVal")
    def put_integer_val(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        value_ = DataDatabricksWorkspaceSettingV2IntegerVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putIntegerVal", [value_]))

    @jsii.member(jsii_name="putPersonalCompute")
    def put_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        value_ = DataDatabricksWorkspaceSettingV2PersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putPersonalCompute", [value_]))

    @jsii.member(jsii_name="putRestrictWorkspaceAdmins")
    def put_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        value = DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putStringVal")
    def put_string_val(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        value_ = DataDatabricksWorkspaceSettingV2StringVal(value=value)

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
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicy")
    def aibi_dashboard_embedding_access_policy(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "aibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomains")
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "aibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspace")
    def automatic_cluster_update_workspace(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "automaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="booleanVal")
    def boolean_val(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2BooleanValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2BooleanValOutputReference", jsii.get(self, "booleanVal"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityMode")
    def default_data_security_mode(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2DefaultDataSecurityModeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2DefaultDataSecurityModeOutputReference", jsii.get(self, "defaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicy")
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomains")
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspace")
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "effectiveAutomaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="effectiveBooleanVal")
    def effective_boolean_val(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveBooleanValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveBooleanValOutputReference", jsii.get(self, "effectiveBooleanVal"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityMode")
    def effective_default_data_security_mode(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference", jsii.get(self, "effectiveDefaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveIntegerVal")
    def effective_integer_val(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveIntegerValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveIntegerValOutputReference", jsii.get(self, "effectiveIntegerVal"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalCompute")
    def effective_personal_compute(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectivePersonalComputeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectivePersonalComputeOutputReference", jsii.get(self, "effectivePersonalCompute"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdmins")
    def effective_restrict_workspace_admins(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference", jsii.get(self, "effectiveRestrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="effectiveStringVal")
    def effective_string_val(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveStringValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveStringValOutputReference", jsii.get(self, "effectiveStringVal"))

    @builtins.property
    @jsii.member(jsii_name="integerVal")
    def integer_val(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2IntegerValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2IntegerValOutputReference", jsii.get(self, "integerVal"))

    @builtins.property
    @jsii.member(jsii_name="personalCompute")
    def personal_compute(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2PersonalComputeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2PersonalComputeOutputReference", jsii.get(self, "personalCompute"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdmins")
    def restrict_workspace_admins(
        self,
    ) -> "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdminsOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdminsOutputReference", jsii.get(self, "restrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="stringVal")
    def string_val(self) -> "DataDatabricksWorkspaceSettingV2StringValOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2StringValOutputReference", jsii.get(self, "stringVal"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicyInput")
    def aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "aibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomainsInput")
    def aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "aibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspaceInput")
    def automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace"]], jsii.get(self, "automaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="booleanValInput")
    def boolean_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2BooleanVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2BooleanVal"]], jsii.get(self, "booleanValInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityModeInput")
    def default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode"]], jsii.get(self, "defaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicyInput")
    def effective_aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomainsInput")
    def effective_aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspaceInput")
    def effective_automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]], jsii.get(self, "effectiveAutomaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityModeInput")
    def effective_default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode"]], jsii.get(self, "effectiveDefaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalComputeInput")
    def effective_personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectivePersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectivePersonalCompute"]], jsii.get(self, "effectivePersonalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdminsInput")
    def effective_restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]], jsii.get(self, "effectiveRestrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="integerValInput")
    def integer_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2IntegerVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2IntegerVal"]], jsii.get(self, "integerValInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="personalComputeInput")
    def personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2PersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2PersonalCompute"]], jsii.get(self, "personalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdminsInput")
    def restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins"]], jsii.get(self, "restrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="stringValInput")
    def string_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2StringVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2StringVal"]], jsii.get(self, "stringValInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ee18506ee5e47efbe2cdcb6737aecb93a35f4f6d16d34ab9001cd9aedd1f92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33e625e6b848bf0a868b483891697daa4880ac9012706cdc62e2cc12b8b1f1f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68ca95c1ff236a32c6e3f0c89b8a0d8a0a1cd00f285246f287fb06ea351fc8de)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d25ba2be9d5cb2a8a35f7028523e54b6a3254d2f33cf1624a60e0791f9b2473e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c48c448e537d9c9519bb5aac726ce95ccfb1ec1811e2993efff9d6545d280ac6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3af555f1d0aa9e6b90ca9784c072dc484566867d9d5b6854d02e8b97b7c12ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5e374f28dfc97b52ce870b7222503509c291ebe1cfc0d7caf5c7a31e94b0a54)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fed686675ec77f5d77c9e933fd9b53d30e0f827b5f3cfec04e52c50d0306d5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__71ecd24e7625a3afdf1adb7c6f5d64320677d42bb722a4cb2bc26043c11a84bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245b9e2da7067e6ebdb4b15188bab2dcc1983b81eab131439b1d9e3754089cf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__508de337546acc4128e25e18cfa7eed2748955b8fe7454edd77132424d01822d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4377141697c780a2e2611cd8ed247d81f7b501376809eaed6077fb4c030ce34)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb27d04a1531ffb56510b79c6b0d4d6953aa56d97674dfcf3a825e5b3d590648)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a7ef11b678fe85b28160f9dda91f71b10668972b18e7f4d2a458d1ed3588905)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a38a7080a76125af0425386db15c11128e3881c398b9ca6583bc6fa7cb9c4926)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b481c4f9dfec3a6eaa8eb16a002f9d59378f14011bb82e17fba07bb785f76c10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5ff194b63db396a852d29e936c3184089bc3e733eaf8403e4e62140d2cc17b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e49ba576be5620988436871b1508cf2c156c48fb84856b6964c477f6b46941)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee61d13bcd813c0487c94363f9e1f0dfb4272b5be6a2387bbdf52736214fe240)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.
        '''
        value = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e470d0bb7deaae388b0cceee55a3b54d33129d16c0ece7f0a39be4e29141ca83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8219093c835e5723a0b99e350c6416bcf0b7c0b111a9fb544776f8ca37aea84c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__937951714b72c16a497550cf96592ca30316bd22ab4fbcd0d881ebfdaab29ab8)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.
        '''
        value = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90f5716df4b6b499bf7e5211696a68c5dd1fec5e1328d150efd3bba6097c986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__768c9467cd868fbc0bb82e72881cce805a3d52b7abd0c455b736424d19f6913b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e50f75f9bc640e1094ee2f2c744f01c1b9401eb074747a014920ffa47faf79e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c35df01b8b6f7eabbbee32715fd7c9ad460729b882b44efc7dcefb2eef9dbf04)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40cdf0dd37f1589d0a43c35c4644edd9cda9695340a58f4bf4f2c314ed3cbfb9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2e5c0b3ccd7c77b094dbd84045768ebaca5555d201c7cd7123a2cbc95d13cd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d45cee1e98324e00127cfe1a9815d76571538684916bab74d75ccccdb98d0b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff34d4e01aa609a1f7068ee7562cc55d8befed59517896950df87f01ad8c31ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9b43fc84ff34e00e0ab33314e36ba779f6ef11afa419dcbd5c493ee029d3019)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.
        '''
        value = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b273fd7b5f74a000480cc8496a3c0566a3c816c4182abdc3e28b8a363a89575c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__247e814e13561522eea6ab437c9ef397924fa358b43551cfc6160096326aacba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16a81e7aa29c9d36243da842111f1eeabbb13354ed9b59e5171fd5281ab0781a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8406e282820f301dffa396083c366a4fc6a98504b13a654f28373f041b4d6bbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2BooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2BooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4893e8f4aa8143ae14f15f3b27c54d91435e66aeb7def92dfc81fb8c4c989cab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2BooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2BooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2BooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8278fe52fa761564ea72133a3ead08ed1c725846233529159bcd369e8fea1511)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f869b518dbce9174f58975391bed82df2463e62fece353812b8a621769cc4090)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2BooleanVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2BooleanVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2BooleanVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__217a308c36401200d8fa1c80f744ba14d479558ca7cb59c778993ef7c248e830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2Config",
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
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksWorkspaceSettingV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#boolean_val DataDatabricksWorkspaceSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#default_data_security_mode DataDatabricksWorkspaceSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_default_data_security_mode DataDatabricksWorkspaceSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_personal_compute DataDatabricksWorkspaceSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_restrict_workspace_admins DataDatabricksWorkspaceSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#integer_val DataDatabricksWorkspaceSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#name DataDatabricksWorkspaceSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#personal_compute DataDatabricksWorkspaceSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restrict_workspace_admins DataDatabricksWorkspaceSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#string_val DataDatabricksWorkspaceSettingV2#string_val}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#workspace_id DataDatabricksWorkspaceSettingV2#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aibi_dashboard_embedding_access_policy, dict):
            aibi_dashboard_embedding_access_policy = DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(**aibi_dashboard_embedding_access_policy)
        if isinstance(aibi_dashboard_embedding_approved_domains, dict):
            aibi_dashboard_embedding_approved_domains = DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(**aibi_dashboard_embedding_approved_domains)
        if isinstance(automatic_cluster_update_workspace, dict):
            automatic_cluster_update_workspace = DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace(**automatic_cluster_update_workspace)
        if isinstance(boolean_val, dict):
            boolean_val = DataDatabricksWorkspaceSettingV2BooleanVal(**boolean_val)
        if isinstance(default_data_security_mode, dict):
            default_data_security_mode = DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode(**default_data_security_mode)
        if isinstance(effective_aibi_dashboard_embedding_access_policy, dict):
            effective_aibi_dashboard_embedding_access_policy = DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(**effective_aibi_dashboard_embedding_access_policy)
        if isinstance(effective_aibi_dashboard_embedding_approved_domains, dict):
            effective_aibi_dashboard_embedding_approved_domains = DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(**effective_aibi_dashboard_embedding_approved_domains)
        if isinstance(effective_automatic_cluster_update_workspace, dict):
            effective_automatic_cluster_update_workspace = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(**effective_automatic_cluster_update_workspace)
        if isinstance(effective_default_data_security_mode, dict):
            effective_default_data_security_mode = DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode(**effective_default_data_security_mode)
        if isinstance(effective_personal_compute, dict):
            effective_personal_compute = DataDatabricksWorkspaceSettingV2EffectivePersonalCompute(**effective_personal_compute)
        if isinstance(effective_restrict_workspace_admins, dict):
            effective_restrict_workspace_admins = DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(**effective_restrict_workspace_admins)
        if isinstance(integer_val, dict):
            integer_val = DataDatabricksWorkspaceSettingV2IntegerVal(**integer_val)
        if isinstance(personal_compute, dict):
            personal_compute = DataDatabricksWorkspaceSettingV2PersonalCompute(**personal_compute)
        if isinstance(restrict_workspace_admins, dict):
            restrict_workspace_admins = DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins(**restrict_workspace_admins)
        if isinstance(string_val, dict):
            string_val = DataDatabricksWorkspaceSettingV2StringVal(**string_val)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5fff124ed83a41377c35f90e2ecb261279e1f8e48420074936ad9b79394f6b5)
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
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
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
    def aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy], result)

    @builtins.property
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains], result)

    @builtins.property
    def automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#automatic_cluster_update_workspace}.'''
        result = self._values.get("automatic_cluster_update_workspace")
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace], result)

    @builtins.property
    def boolean_val(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2BooleanVal]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#boolean_val DataDatabricksWorkspaceSettingV2#boolean_val}.'''
        result = self._values.get("boolean_val")
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2BooleanVal], result)

    @builtins.property
    def default_data_security_mode(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#default_data_security_mode DataDatabricksWorkspaceSettingV2#default_data_security_mode}.'''
        result = self._values.get("default_data_security_mode")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains DataDatabricksWorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"], result)

    @builtins.property
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_automatic_cluster_update_workspace DataDatabricksWorkspaceSettingV2#effective_automatic_cluster_update_workspace}.'''
        result = self._values.get("effective_automatic_cluster_update_workspace")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"], result)

    @builtins.property
    def effective_default_data_security_mode(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_default_data_security_mode DataDatabricksWorkspaceSettingV2#effective_default_data_security_mode}.'''
        result = self._values.get("effective_default_data_security_mode")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode"], result)

    @builtins.property
    def effective_personal_compute(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectivePersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_personal_compute DataDatabricksWorkspaceSettingV2#effective_personal_compute}.'''
        result = self._values.get("effective_personal_compute")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectivePersonalCompute"], result)

    @builtins.property
    def effective_restrict_workspace_admins(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#effective_restrict_workspace_admins DataDatabricksWorkspaceSettingV2#effective_restrict_workspace_admins}.'''
        result = self._values.get("effective_restrict_workspace_admins")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"], result)

    @builtins.property
    def integer_val(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2IntegerVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#integer_val DataDatabricksWorkspaceSettingV2#integer_val}.'''
        result = self._values.get("integer_val")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2IntegerVal"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#name DataDatabricksWorkspaceSettingV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personal_compute(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2PersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#personal_compute DataDatabricksWorkspaceSettingV2#personal_compute}.'''
        result = self._values.get("personal_compute")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2PersonalCompute"], result)

    @builtins.property
    def restrict_workspace_admins(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restrict_workspace_admins DataDatabricksWorkspaceSettingV2#restrict_workspace_admins}.'''
        result = self._values.get("restrict_workspace_admins")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins"], result)

    @builtins.property
    def string_val(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2StringVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#string_val DataDatabricksWorkspaceSettingV2#string_val}.'''
        result = self._values.get("string_val")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2StringVal"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#workspace_id DataDatabricksWorkspaceSettingV2#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6fedec57d7ee8812a7f0dbc19dc0f1400c2db1c5d30c0b7a3b14fb8a9031014)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2DefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2DefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3e3e23a13978cd279a3344ad2feec35e43c8055695f8e573d79602f0b60dec9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f88d51ec1b25062fd18526da795033750f823dfb8c5fd3dd05aacd27f8ccaeaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cee322b892a77fa43bf2963de0c520e6bac1079af1cd1a8af854ffc347f2a3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9b53648256ad1e0a288b246c3240e232a12310359093799b3a8f16e36b19cfa)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#access_policy_type DataDatabricksWorkspaceSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__42b96a8b8c6243687cda647637c66127f749ccfff846560abd3f8a75fed5c3e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6d57adac93eb0d560e0bd85b23dd7ac40ed4d2f3ffd34c4c6b9b25a30b6f115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96e662d2224b71b4416c414263e65ffc2743d3f930ea9044077ae7c2fdb37a7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95351e81843704ae74c4f6b4a112eb2e6cbb36b5996ca0da9464ea7b29db081c)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#approved_domains DataDatabricksWorkspaceSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef7d04b58cb690d5807afec5e7b8f10c26032c2cfa7756949ca67db2d9ce9a4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9e9220bb6375871f42e015557f93e243a7c0f3ada5020f7c2f63e095287328e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40e5946f2af8f03ba14d4d15543a0d878b7689f211d85caf3018afa0c599a29d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca62af87357c687e493357e1da0e023476eed8cf3fa15ce65d92d6af5c4ee4e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#can_toggle DataDatabricksWorkspaceSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enabled DataDatabricksWorkspaceSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#enablement_details DataDatabricksWorkspaceSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#maintenance_window DataDatabricksWorkspaceSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#restart_even_if_no_updates_available DataDatabricksWorkspaceSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4dee643fb59eae86dba88404fd58cc8fbdb9718f78761789121a8ee0d527e59)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a164bac60a4d0efdd09789c0bcf80b3e86991aa2c63c1b30bf6556f0b46aee7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a6268b410de2503bd8b5be3bfcfd79c3d1506e89746bf240061511aa71515f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c50ba59517f13701546b74cfdeb2eb97410854a1880211a3ed7ef1bf077b18ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf9636fc71a7d85f683d6b426a30b5b52fd65dbb4aa34fd21e0d404e45c6dfb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d0c82375c1c9a433900e7706083428a6c74ebeb9c8c0389c463a2d92e7f3e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fa6e5fbd13dadd36c370527cbe615d104c05c187b6f87c1abca90a79f11073d)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3305ce7f1666a4e02a212bc2c4d56681e0ac8442628be8bf1b2ff933d917b437)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__053785444ad37f478c3c61e8865f4be8c1fcd225aab3c5261e4697ba3472a1cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beae0f9ece3a4a7055c13800469b0d9fbc4b762e4f677675b714afd415384116)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#day_of_week DataDatabricksWorkspaceSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#frequency DataDatabricksWorkspaceSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#window_start_time DataDatabricksWorkspaceSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e0fa08421632d1ecbdad125c5b834c35335a67a98cb14645f4e2b6b55870efb)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381645bea637d984a62e3701354c2e692a97208bca4311321734cf4ca1397242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__933c44403a6bbcd6ec0642d8dac7a1cc6790fca74299319cf4b2aba7db064640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40ef30ad0b9bbb19f3de259e3bf80f786c42372f6fca519f5e8a852b27f6da33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60851b85b75c26560009eee2cd55c451826535bedad0b6d549e0b8113bffc856)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#hours DataDatabricksWorkspaceSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#minutes DataDatabricksWorkspaceSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4df66e2a89ba8ace127f86f54a5d1271895c34ebd35270fa0442812bfc83eae9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__46fd06b972d7c3f93f66a662ed45c024b85977c0fec18c6b4c57abcad9c3aad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a14c8345b71dff469f6548c95f882688d4985b9ca15b9e210a0091ec134c319)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecdf48a5b02cf3661dd87abea07f00c3c2e882d008c2b8fbfed3a1cb96b418c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36da4f4e6a921371de6b8b363c796850f07260f6e7245b11d9e4393ea7bd7e2f)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#forced_for_compliance_mode DataDatabricksWorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_disabled_entitlement DataDatabricksWorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#unavailable_for_non_enterprise_tier DataDatabricksWorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#week_day_based_schedule DataDatabricksWorkspaceSettingV2#week_day_based_schedule}.
        '''
        value = DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__a379c96639718e746ebb7a873c60ae3f41ee116b9d5490543744b8c4fddedcc4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9e4cdc1ca42fe0b26ca7ec5d5a1314cab85a5673338f4c8d764f82d79eceb46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aae51efc4a3e6a0b881fb1727e9557a545b71fc6d60bdcd30b5ab99a2f233c47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9299053bdae728ebbe1c39aec217ecee56c7d2edddbbf4306889e4fa8388d7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveBooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2EffectiveBooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2f4f626aaf93b76dd02b6c6620e63c873d26081fff64ce039601a223288d3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveBooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveBooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveBooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__402eb68a34e46d387082a034d43744d83965e4a44443969f4852b0e379b406d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c7dde54978ee6a2846fab5f6dc257e716164d49ec44d067b76d6c1f80a5b52c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveBooleanVal]:
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveBooleanVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveBooleanVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__949407c960ed1fe85f17c68d51da722d1bdc3fd3ea443a66168e18a1cf412ea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0861886b37389f91f94140bde83ed476c43a568c53a1ee8745158185bdc0d61c)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d64107dcd4a52a3b86c35dc20cc0bffa88919f6869669a886f04855178d8de3e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b90130bda2dd640ef5ea93f498fa5d886d3aa415fc971fd35892f0ddbc0443ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61b935233c9b3701d075bf2e533fe8f32935b363e5480a4d192b9cbb914fbc20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveIntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2EffectiveIntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddfbf854676ac9edf33c47c57d07105bde63066fabdfb811d920d0df032edf3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveIntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveIntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveIntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a46243272dde3bb181a036d4fae5a75d4dd50a9c22384c70af7c902a4f636e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5e933ce03a181c3100ded15ae7f4c03c6f4db618ea3f4055ab32b47e24e56f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveIntegerVal]:
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveIntegerVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveIntegerVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64bd84821b3d71900d743098782771265707964d43b11f542b6b4f771379e3cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectivePersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2EffectivePersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f76460e2d7dd3f7a4c153281c5a8fca7238e70ae71bcd71d14817cae6a04b05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectivePersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectivePersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectivePersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa2b2232ea049fadab093a393f5a67c0b43306c5d4ab2c1d03ea34ed715f7fb3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0dbe3271c34d1f4a26a46b5a568000de4a48aa36f8c9d9036f7c565c29d95e8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectivePersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectivePersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectivePersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd7167327d623e377abc9633d480f41762b88135123d8cfde2bfbc9acc609e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__786b845cde6cb2649d108569eef67c5e98130ccee684da6ebb3369201635af39)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d3788243d178be6eb9c566bd511e65a4579892428d598693d1b68df9226152f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fd9e6bf7e9b7243ebda5d73d2ca060df2db085bf9b94535b31e250c18fcd72f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d527b738692dd6e991a74efd4a4e56af9b451eb9b0906af93d7a5f9a56e5ee1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveStringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2EffectiveStringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10541eed65b1fcb0428abddb36d510a2512f4f76d67aab293b477bebaea63c3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2EffectiveStringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2EffectiveStringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2EffectiveStringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bab7c0f885546165f4e192af8d3f2e7c3aef45ee77eb09529c5094231b8e60af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a05870246564c0a38cc166a65a8cbe7f05b114fd61260c68e449f7938f24719)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveStringVal]:
        return typing.cast(typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveStringVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveStringVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5248a6cca5ae53b309de72c48925d108335b9c6321e00977bc16040cd17553f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2IntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2IntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed76f241435562f5e6b565b089a1896f1224f23745b1820498ead733187ddc7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2IntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2IntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2IntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3dff6ecb4bff63c3cd5a39e3b24bea75cf831427a53a576c47593f7f45ab05dd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02de9eeafa044e3de33e6ac0950aad451976fb94169e6232dd71a6ae0dfb58e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2IntegerVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2IntegerVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2IntegerVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a36ff019aa9531465e7af07631185e92fd9181c64c61bdd7e686f064d8933c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2PersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2PersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa83610ed5fe52a377000282a2a49903e7dfd05e182039247d0190bad57cdaf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2PersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2PersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2PersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9b4fbb42db87f90a6d049aef5d7d210f0a631f3519c338975d7dcf138ba2c88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2aaa770eb8187c0a3c9566f293b031807e7914539fda79eac49bfbb5395fca0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2PersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2PersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2PersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac375a407a41d2160ad5b720c81252a903e7c672e10e5e335f6ef635134dd6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7832d1b0aa3794e6334746cf52617f05855aea727cfad96ca43a901bdc84646d)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#status DataDatabricksWorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9cee2903dfc06b1535d0ad1f51d9ea8a36b4b20800c72ac3185ac3b67cc050c1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f7d81f04a68d57dfc0ca9d385608a767b8763571c3b3e6bd033e154fc15a6bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d46d5ab6c4856f320314a4ceefc64e5e116791483cd0fa42142eee049e02d83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2StringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class DataDatabricksWorkspaceSettingV2StringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e4fc626dcae91ec19eeee8eb950ea075ddccbe944b4bd7d41b9603ecd90c54b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/workspace_setting_v2#value DataDatabricksWorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksWorkspaceSettingV2StringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksWorkspaceSettingV2StringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksWorkspaceSettingV2.DataDatabricksWorkspaceSettingV2StringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7547f068ce15d18da8622015cec1b68cb463f0aec0341d0b9a7095d4234bd08e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__69f1f156bd005c3fc7bbdd25b98457ba693466387f2fb6e01f616eae32879960)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2StringVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2StringVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2StringVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__890c7bccb02feb24fc6e3a104e1c5fe52194507d472da6773cc15c19e1919b64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksWorkspaceSettingV2",
    "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy",
    "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
    "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains",
    "DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
    "DataDatabricksWorkspaceSettingV2BooleanVal",
    "DataDatabricksWorkspaceSettingV2BooleanValOutputReference",
    "DataDatabricksWorkspaceSettingV2Config",
    "DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode",
    "DataDatabricksWorkspaceSettingV2DefaultDataSecurityModeOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    "DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveBooleanVal",
    "DataDatabricksWorkspaceSettingV2EffectiveBooleanValOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode",
    "DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveIntegerVal",
    "DataDatabricksWorkspaceSettingV2EffectiveIntegerValOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectivePersonalCompute",
    "DataDatabricksWorkspaceSettingV2EffectivePersonalComputeOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins",
    "DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
    "DataDatabricksWorkspaceSettingV2EffectiveStringVal",
    "DataDatabricksWorkspaceSettingV2EffectiveStringValOutputReference",
    "DataDatabricksWorkspaceSettingV2IntegerVal",
    "DataDatabricksWorkspaceSettingV2IntegerValOutputReference",
    "DataDatabricksWorkspaceSettingV2PersonalCompute",
    "DataDatabricksWorkspaceSettingV2PersonalComputeOutputReference",
    "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins",
    "DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdminsOutputReference",
    "DataDatabricksWorkspaceSettingV2StringVal",
    "DataDatabricksWorkspaceSettingV2StringValOutputReference",
]

publication.publish()

def _typecheckingstub__3a2bad695c9beaab56f98c083650ac90d0a53857e7b080801d8f176796eef96a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__5b0cfb6b27440205520c2c43f485b695b806c61141e3251e02a440152da852fb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ee18506ee5e47efbe2cdcb6737aecb93a35f4f6d16d34ab9001cd9aedd1f92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33e625e6b848bf0a868b483891697daa4880ac9012706cdc62e2cc12b8b1f1f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68ca95c1ff236a32c6e3f0c89b8a0d8a0a1cd00f285246f287fb06ea351fc8de(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d25ba2be9d5cb2a8a35f7028523e54b6a3254d2f33cf1624a60e0791f9b2473e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c48c448e537d9c9519bb5aac726ce95ccfb1ec1811e2993efff9d6545d280ac6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3af555f1d0aa9e6b90ca9784c072dc484566867d9d5b6854d02e8b97b7c12ebb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5e374f28dfc97b52ce870b7222503509c291ebe1cfc0d7caf5c7a31e94b0a54(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fed686675ec77f5d77c9e933fd9b53d30e0f827b5f3cfec04e52c50d0306d5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ecd24e7625a3afdf1adb7c6f5d64320677d42bb722a4cb2bc26043c11a84bb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245b9e2da7067e6ebdb4b15188bab2dcc1983b81eab131439b1d9e3754089cf6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__508de337546acc4128e25e18cfa7eed2748955b8fe7454edd77132424d01822d(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4377141697c780a2e2611cd8ed247d81f7b501376809eaed6077fb4c030ce34(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb27d04a1531ffb56510b79c6b0d4d6953aa56d97674dfcf3a825e5b3d590648(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a7ef11b678fe85b28160f9dda91f71b10668972b18e7f4d2a458d1ed3588905(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38a7080a76125af0425386db15c11128e3881c398b9ca6583bc6fa7cb9c4926(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b481c4f9dfec3a6eaa8eb16a002f9d59378f14011bb82e17fba07bb785f76c10(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ff194b63db396a852d29e936c3184089bc3e733eaf8403e4e62140d2cc17b9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e49ba576be5620988436871b1508cf2c156c48fb84856b6964c477f6b46941(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee61d13bcd813c0487c94363f9e1f0dfb4272b5be6a2387bbdf52736214fe240(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e470d0bb7deaae388b0cceee55a3b54d33129d16c0ece7f0a39be4e29141ca83(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8219093c835e5723a0b99e350c6416bcf0b7c0b111a9fb544776f8ca37aea84c(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937951714b72c16a497550cf96592ca30316bd22ab4fbcd0d881ebfdaab29ab8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90f5716df4b6b499bf7e5211696a68c5dd1fec5e1328d150efd3bba6097c986(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__768c9467cd868fbc0bb82e72881cce805a3d52b7abd0c455b736424d19f6913b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e50f75f9bc640e1094ee2f2c744f01c1b9401eb074747a014920ffa47faf79e6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35df01b8b6f7eabbbee32715fd7c9ad460729b882b44efc7dcefb2eef9dbf04(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40cdf0dd37f1589d0a43c35c4644edd9cda9695340a58f4bf4f2c314ed3cbfb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e5c0b3ccd7c77b094dbd84045768ebaca5555d201c7cd7123a2cbc95d13cd1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d45cee1e98324e00127cfe1a9815d76571538684916bab74d75ccccdb98d0b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff34d4e01aa609a1f7068ee7562cc55d8befed59517896950df87f01ad8c31ea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b43fc84ff34e00e0ab33314e36ba779f6ef11afa419dcbd5c493ee029d3019(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b273fd7b5f74a000480cc8496a3c0566a3c816c4182abdc3e28b8a363a89575c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__247e814e13561522eea6ab437c9ef397924fa358b43551cfc6160096326aacba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a81e7aa29c9d36243da842111f1eeabbb13354ed9b59e5171fd5281ab0781a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8406e282820f301dffa396083c366a4fc6a98504b13a654f28373f041b4d6bbd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4893e8f4aa8143ae14f15f3b27c54d91435e66aeb7def92dfc81fb8c4c989cab(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8278fe52fa761564ea72133a3ead08ed1c725846233529159bcd369e8fea1511(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f869b518dbce9174f58975391bed82df2463e62fece353812b8a621769cc4090(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__217a308c36401200d8fa1c80f744ba14d479558ca7cb59c778993ef7c248e830(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2BooleanVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5fff124ed83a41377c35f90e2ecb261279e1f8e48420074936ad9b79394f6b5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fedec57d7ee8812a7f0dbc19dc0f1400c2db1c5d30c0b7a3b14fb8a9031014(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e3e23a13978cd279a3344ad2feec35e43c8055695f8e573d79602f0b60dec9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88d51ec1b25062fd18526da795033750f823dfb8c5fd3dd05aacd27f8ccaeaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cee322b892a77fa43bf2963de0c520e6bac1079af1cd1a8af854ffc347f2a3f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2DefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b53648256ad1e0a288b246c3240e232a12310359093799b3a8f16e36b19cfa(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42b96a8b8c6243687cda647637c66127f749ccfff846560abd3f8a75fed5c3e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d57adac93eb0d560e0bd85b23dd7ac40ed4d2f3ffd34c4c6b9b25a30b6f115(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96e662d2224b71b4416c414263e65ffc2743d3f930ea9044077ae7c2fdb37a7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95351e81843704ae74c4f6b4a112eb2e6cbb36b5996ca0da9464ea7b29db081c(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef7d04b58cb690d5807afec5e7b8f10c26032c2cfa7756949ca67db2d9ce9a4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e9220bb6375871f42e015557f93e243a7c0f3ada5020f7c2f63e095287328e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e5946f2af8f03ba14d4d15543a0d878b7689f211d85caf3018afa0c599a29d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca62af87357c687e493357e1da0e023476eed8cf3fa15ce65d92d6af5c4ee4e(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4dee643fb59eae86dba88404fd58cc8fbdb9718f78761789121a8ee0d527e59(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a164bac60a4d0efdd09789c0bcf80b3e86991aa2c63c1b30bf6556f0b46aee7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6268b410de2503bd8b5be3bfcfd79c3d1506e89746bf240061511aa71515f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50ba59517f13701546b74cfdeb2eb97410854a1880211a3ed7ef1bf077b18ce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf9636fc71a7d85f683d6b426a30b5b52fd65dbb4aa34fd21e0d404e45c6dfb8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d0c82375c1c9a433900e7706083428a6c74ebeb9c8c0389c463a2d92e7f3e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fa6e5fbd13dadd36c370527cbe615d104c05c187b6f87c1abca90a79f11073d(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3305ce7f1666a4e02a212bc2c4d56681e0ac8442628be8bf1b2ff933d917b437(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__053785444ad37f478c3c61e8865f4be8c1fcd225aab3c5261e4697ba3472a1cf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beae0f9ece3a4a7055c13800469b0d9fbc4b762e4f677675b714afd415384116(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e0fa08421632d1ecbdad125c5b834c35335a67a98cb14645f4e2b6b55870efb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381645bea637d984a62e3701354c2e692a97208bca4311321734cf4ca1397242(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__933c44403a6bbcd6ec0642d8dac7a1cc6790fca74299319cf4b2aba7db064640(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ef30ad0b9bbb19f3de259e3bf80f786c42372f6fca519f5e8a852b27f6da33(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60851b85b75c26560009eee2cd55c451826535bedad0b6d549e0b8113bffc856(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4df66e2a89ba8ace127f86f54a5d1271895c34ebd35270fa0442812bfc83eae9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46fd06b972d7c3f93f66a662ed45c024b85977c0fec18c6b4c57abcad9c3aad2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a14c8345b71dff469f6548c95f882688d4985b9ca15b9e210a0091ec134c319(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecdf48a5b02cf3661dd87abea07f00c3c2e882d008c2b8fbfed3a1cb96b418c9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36da4f4e6a921371de6b8b363c796850f07260f6e7245b11d9e4393ea7bd7e2f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a379c96639718e746ebb7a873c60ae3f41ee116b9d5490543744b8c4fddedcc4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9e4cdc1ca42fe0b26ca7ec5d5a1314cab85a5673338f4c8d764f82d79eceb46(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae51efc4a3e6a0b881fb1727e9557a545b71fc6d60bdcd30b5ab99a2f233c47(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9299053bdae728ebbe1c39aec217ecee56c7d2edddbbf4306889e4fa8388d7f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2f4f626aaf93b76dd02b6c6620e63c873d26081fff64ce039601a223288d3d(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__402eb68a34e46d387082a034d43744d83965e4a44443969f4852b0e379b406d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7dde54978ee6a2846fab5f6dc257e716164d49ec44d067b76d6c1f80a5b52c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__949407c960ed1fe85f17c68d51da722d1bdc3fd3ea443a66168e18a1cf412ea1(
    value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveBooleanVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0861886b37389f91f94140bde83ed476c43a568c53a1ee8745158185bdc0d61c(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64107dcd4a52a3b86c35dc20cc0bffa88919f6869669a886f04855178d8de3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b90130bda2dd640ef5ea93f498fa5d886d3aa415fc971fd35892f0ddbc0443ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b935233c9b3701d075bf2e533fe8f32935b363e5480a4d192b9cbb914fbc20(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveDefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddfbf854676ac9edf33c47c57d07105bde63066fabdfb811d920d0df032edf3d(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a46243272dde3bb181a036d4fae5a75d4dd50a9c22384c70af7c902a4f636e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5e933ce03a181c3100ded15ae7f4c03c6f4db618ea3f4055ab32b47e24e56f2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64bd84821b3d71900d743098782771265707964d43b11f542b6b4f771379e3cc(
    value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveIntegerVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f76460e2d7dd3f7a4c153281c5a8fca7238e70ae71bcd71d14817cae6a04b05(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2b2232ea049fadab093a393f5a67c0b43306c5d4ab2c1d03ea34ed715f7fb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dbe3271c34d1f4a26a46b5a568000de4a48aa36f8c9d9036f7c565c29d95e8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd7167327d623e377abc9633d480f41762b88135123d8cfde2bfbc9acc609e1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectivePersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__786b845cde6cb2649d108569eef67c5e98130ccee684da6ebb3369201635af39(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d3788243d178be6eb9c566bd511e65a4579892428d598693d1b68df9226152f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fd9e6bf7e9b7243ebda5d73d2ca060df2db085bf9b94535b31e250c18fcd72f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d527b738692dd6e991a74efd4a4e56af9b451eb9b0906af93d7a5f9a56e5ee1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10541eed65b1fcb0428abddb36d510a2512f4f76d67aab293b477bebaea63c3d(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab7c0f885546165f4e192af8d3f2e7c3aef45ee77eb09529c5094231b8e60af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a05870246564c0a38cc166a65a8cbe7f05b114fd61260c68e449f7938f24719(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5248a6cca5ae53b309de72c48925d108335b9c6321e00977bc16040cd17553f(
    value: typing.Optional[DataDatabricksWorkspaceSettingV2EffectiveStringVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed76f241435562f5e6b565b089a1896f1224f23745b1820498ead733187ddc7d(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dff6ecb4bff63c3cd5a39e3b24bea75cf831427a53a576c47593f7f45ab05dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02de9eeafa044e3de33e6ac0950aad451976fb94169e6232dd71a6ae0dfb58e6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a36ff019aa9531465e7af07631185e92fd9181c64c61bdd7e686f064d8933c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2IntegerVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa83610ed5fe52a377000282a2a49903e7dfd05e182039247d0190bad57cdaf6(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b4fbb42db87f90a6d049aef5d7d210f0a631f3519c338975d7dcf138ba2c88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2aaa770eb8187c0a3c9566f293b031807e7914539fda79eac49bfbb5395fca0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac375a407a41d2160ad5b720c81252a903e7c672e10e5e335f6ef635134dd6a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2PersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7832d1b0aa3794e6334746cf52617f05855aea727cfad96ca43a901bdc84646d(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cee2903dfc06b1535d0ad1f51d9ea8a36b4b20800c72ac3185ac3b67cc050c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7d81f04a68d57dfc0ca9d385608a767b8763571c3b3e6bd033e154fc15a6bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d46d5ab6c4856f320314a4ceefc64e5e116791483cd0fa42142eee049e02d83(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2RestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4fc626dcae91ec19eeee8eb950ea075ddccbe944b4bd7d41b9603ecd90c54b(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7547f068ce15d18da8622015cec1b68cb463f0aec0341d0b9a7095d4234bd08e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69f1f156bd005c3fc7bbdd25b98457ba693466387f2fb6e01f616eae32879960(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890c7bccb02feb24fc6e3a104e1c5fe52194507d472da6773cc15c19e1919b64(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksWorkspaceSettingV2StringVal]],
) -> None:
    """Type checking stubs"""
    pass
