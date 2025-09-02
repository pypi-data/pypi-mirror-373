r'''
# `databricks_workspace_setting_v2`

Refer to the Terraform Registry for docs: [`databricks_workspace_setting_v2`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2).
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


class WorkspaceSettingV2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2 databricks_workspace_setting_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union["WorkspaceSettingV2BooleanVal", typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["WorkspaceSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["WorkspaceSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["WorkspaceSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["WorkspaceSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["WorkspaceSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["WorkspaceSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2 databricks_workspace_setting_v2} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_access_policy WorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#automatic_cluster_update_workspace WorkspaceSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#boolean_val WorkspaceSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#default_data_security_mode WorkspaceSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy WorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_automatic_cluster_update_workspace WorkspaceSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_default_data_security_mode WorkspaceSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_personal_compute WorkspaceSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_restrict_workspace_admins WorkspaceSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#integer_val WorkspaceSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#name WorkspaceSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#personal_compute WorkspaceSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restrict_workspace_admins WorkspaceSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#string_val WorkspaceSettingV2#string_val}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#workspace_id WorkspaceSettingV2#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f267c4ea4afb3ee8b2f333d2f369563745a9d40b819a9c3ee6943fc5661a6c2c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WorkspaceSettingV2Config(
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
        '''Generates CDKTF code for importing a WorkspaceSettingV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WorkspaceSettingV2 to import.
        :param import_from_id: The id of the existing WorkspaceSettingV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WorkspaceSettingV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e38844a0504ea424c5942d3fe81c158def1c3d1025a993e8658e1cc8d04e823b)
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
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.
        '''
        value = WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.
        '''
        value = WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putAutomaticClusterUpdateWorkspace")
    def put_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        value = WorkspaceSettingV2AutomaticClusterUpdateWorkspace(
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
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        value_ = WorkspaceSettingV2BooleanVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putBooleanVal", [value_]))

    @jsii.member(jsii_name="putDefaultDataSecurityMode")
    def put_default_data_security_mode(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        value = WorkspaceSettingV2DefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectiveAibiDashboardEmbeddingAccessPolicy")
    def put_effective_aibi_dashboard_embedding_access_policy(
        self,
        *,
        access_policy_type: builtins.str,
    ) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.
        '''
        value = WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(
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
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.
        '''
        value = WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(
            approved_domains=approved_domains
        )

        return typing.cast(None, jsii.invoke(self, "putEffectiveAibiDashboardEmbeddingApprovedDomains", [value]))

    @jsii.member(jsii_name="putEffectiveAutomaticClusterUpdateWorkspace")
    def put_effective_automatic_cluster_update_workspace(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        value = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(
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
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        value = WorkspaceSettingV2EffectiveDefaultDataSecurityMode(status=status)

        return typing.cast(None, jsii.invoke(self, "putEffectiveDefaultDataSecurityMode", [value]))

    @jsii.member(jsii_name="putEffectivePersonalCompute")
    def put_effective_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        value_ = WorkspaceSettingV2EffectivePersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putEffectivePersonalCompute", [value_]))

    @jsii.member(jsii_name="putEffectiveRestrictWorkspaceAdmins")
    def put_effective_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        value = WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putEffectiveRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putIntegerVal")
    def put_integer_val(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        value_ = WorkspaceSettingV2IntegerVal(value=value)

        return typing.cast(None, jsii.invoke(self, "putIntegerVal", [value_]))

    @jsii.member(jsii_name="putPersonalCompute")
    def put_personal_compute(
        self,
        *,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        value_ = WorkspaceSettingV2PersonalCompute(value=value)

        return typing.cast(None, jsii.invoke(self, "putPersonalCompute", [value_]))

    @jsii.member(jsii_name="putRestrictWorkspaceAdmins")
    def put_restrict_workspace_admins(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        value = WorkspaceSettingV2RestrictWorkspaceAdmins(status=status)

        return typing.cast(None, jsii.invoke(self, "putRestrictWorkspaceAdmins", [value]))

    @jsii.member(jsii_name="putStringVal")
    def put_string_val(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        value_ = WorkspaceSettingV2StringVal(value=value)

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
    ) -> "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "aibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomains")
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "aibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspace")
    def automatic_cluster_update_workspace(
        self,
    ) -> "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("WorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "automaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="booleanVal")
    def boolean_val(self) -> "WorkspaceSettingV2BooleanValOutputReference":
        return typing.cast("WorkspaceSettingV2BooleanValOutputReference", jsii.get(self, "booleanVal"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityMode")
    def default_data_security_mode(
        self,
    ) -> "WorkspaceSettingV2DefaultDataSecurityModeOutputReference":
        return typing.cast("WorkspaceSettingV2DefaultDataSecurityModeOutputReference", jsii.get(self, "defaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicy")
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicy"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomains")
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference", jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomains"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspace")
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference", jsii.get(self, "effectiveAutomaticClusterUpdateWorkspace"))

    @builtins.property
    @jsii.member(jsii_name="effectiveBooleanVal")
    def effective_boolean_val(
        self,
    ) -> "WorkspaceSettingV2EffectiveBooleanValOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveBooleanValOutputReference", jsii.get(self, "effectiveBooleanVal"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityMode")
    def effective_default_data_security_mode(
        self,
    ) -> "WorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference", jsii.get(self, "effectiveDefaultDataSecurityMode"))

    @builtins.property
    @jsii.member(jsii_name="effectiveIntegerVal")
    def effective_integer_val(
        self,
    ) -> "WorkspaceSettingV2EffectiveIntegerValOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveIntegerValOutputReference", jsii.get(self, "effectiveIntegerVal"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalCompute")
    def effective_personal_compute(
        self,
    ) -> "WorkspaceSettingV2EffectivePersonalComputeOutputReference":
        return typing.cast("WorkspaceSettingV2EffectivePersonalComputeOutputReference", jsii.get(self, "effectivePersonalCompute"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdmins")
    def effective_restrict_workspace_admins(
        self,
    ) -> "WorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference", jsii.get(self, "effectiveRestrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="effectiveStringVal")
    def effective_string_val(
        self,
    ) -> "WorkspaceSettingV2EffectiveStringValOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveStringValOutputReference", jsii.get(self, "effectiveStringVal"))

    @builtins.property
    @jsii.member(jsii_name="integerVal")
    def integer_val(self) -> "WorkspaceSettingV2IntegerValOutputReference":
        return typing.cast("WorkspaceSettingV2IntegerValOutputReference", jsii.get(self, "integerVal"))

    @builtins.property
    @jsii.member(jsii_name="personalCompute")
    def personal_compute(self) -> "WorkspaceSettingV2PersonalComputeOutputReference":
        return typing.cast("WorkspaceSettingV2PersonalComputeOutputReference", jsii.get(self, "personalCompute"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdmins")
    def restrict_workspace_admins(
        self,
    ) -> "WorkspaceSettingV2RestrictWorkspaceAdminsOutputReference":
        return typing.cast("WorkspaceSettingV2RestrictWorkspaceAdminsOutputReference", jsii.get(self, "restrictWorkspaceAdmins"))

    @builtins.property
    @jsii.member(jsii_name="stringVal")
    def string_val(self) -> "WorkspaceSettingV2StringValOutputReference":
        return typing.cast("WorkspaceSettingV2StringValOutputReference", jsii.get(self, "stringVal"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingAccessPolicyInput")
    def aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "aibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="aibiDashboardEmbeddingApprovedDomainsInput")
    def aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "aibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticClusterUpdateWorkspaceInput")
    def automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspace"]], jsii.get(self, "automaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="booleanValInput")
    def boolean_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2BooleanVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2BooleanVal"]], jsii.get(self, "booleanValInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultDataSecurityModeInput")
    def default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2DefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2DefaultDataSecurityMode"]], jsii.get(self, "defaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingAccessPolicyInput")
    def effective_aibi_dashboard_embedding_access_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]], jsii.get(self, "effectiveAibiDashboardEmbeddingAccessPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAibiDashboardEmbeddingApprovedDomainsInput")
    def effective_aibi_dashboard_embedding_approved_domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]], jsii.get(self, "effectiveAibiDashboardEmbeddingApprovedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveAutomaticClusterUpdateWorkspaceInput")
    def effective_automatic_cluster_update_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]], jsii.get(self, "effectiveAutomaticClusterUpdateWorkspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveDefaultDataSecurityModeInput")
    def effective_default_data_security_mode_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveDefaultDataSecurityMode"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveDefaultDataSecurityMode"]], jsii.get(self, "effectiveDefaultDataSecurityModeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectivePersonalComputeInput")
    def effective_personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectivePersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectivePersonalCompute"]], jsii.get(self, "effectivePersonalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveRestrictWorkspaceAdminsInput")
    def effective_restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]], jsii.get(self, "effectiveRestrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="integerValInput")
    def integer_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2IntegerVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2IntegerVal"]], jsii.get(self, "integerValInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="personalComputeInput")
    def personal_compute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2PersonalCompute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2PersonalCompute"]], jsii.get(self, "personalComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictWorkspaceAdminsInput")
    def restrict_workspace_admins_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2RestrictWorkspaceAdmins"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2RestrictWorkspaceAdmins"]], jsii.get(self, "restrictWorkspaceAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="stringValInput")
    def string_val_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2StringVal"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2StringVal"]], jsii.get(self, "stringValInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b504a46d417967fd0e842f4df21c8d3b5728cbe2886e3b9b82f5721c0004c050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da970c4a98bbfbb138a79343d967aadbaa8e3a58b17a0d946e88c8c64abd9873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad7d3498e7e42a46ce17411ad2257a8dfcc7b4a9d5e63cbcbb81417076a62707)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85afabce50ea404b9bee9057fac3e04a6142077dcc93240bb31421cdb5c6de88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52a718ee456f778df5d388faa81c61230f6addd1b2c494b806edfeb396f450ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cafeff69ee98d9ad30919416883511c67b54f21b7ade83e172ca1db7fa27c0e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e904ae13b024580fefd5b554aab0abe4436b145f99e0270d638b33ffa25d4e9f)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__687c11bfca12ae94a8ad7a503f9ef98c38fefe741a2fd4d275c3a62e723cb972)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c7849e7134eaf63d7fca98164dd5aa3a3cd6185b809dbf096e7262dd0a99001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3c53c08e1ff0d131af6b2e00146b1655782e63bf74622c612c36a5a87c1cc32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class WorkspaceSettingV2AutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692c0551b5180577ed48d5b302c0590a6fa5ffacffa7a4c0c34063fe69940914)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c968c0ca28a18853263c08ecc0f59c92ebd99c7e87d0bc4cb30205549df8fd48)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d61723d20fbec84d160c6154327d7cdc50e7dbc9af01c705f069e666e82f76e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8504d9b01b6747de1df9900505792c81e1f84e679ee9d1c3a2a337c50e5baf1d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a0c57bad1b610d3868ba98c411b921932991f9ea4ec24fbc80dcf30d6f37d35)
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
            type_hints = typing.get_type_hints(_typecheckingstub__862c3e35beacd440d0c0dded98b4d8aaace7d767d0aa7a82beca18e754ea927c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da2be8d34f7ecad0d5992bffe6ff8e4ad3146fcc753fc6e3f916fe1a2ca752a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__634cfb55242b35f404abfc640248b2cacbfe7cdba7b6674e6df77c4694df318a)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab113f15e4fffdb42794d555f12c842ac3afa92ef22a4c1e7687e635339b97a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.
        '''
        value = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1994eda3c9c0a63459da88a744ff338c6c24ea4460903c6adb0f8ec834506c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955f6d4eb41c930a9b9ee5bbe61f4b80c31e62320d0c2a441f7b185d1d6b93c0)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40920a97f7e4e6d9b908171044582c6ff6cb617e48e89277e1341ee73be99733)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.
        '''
        value = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a6f22a7ef4dfbee17b4905d07289d3378f420cba8109341ea21315934e92e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae2b243a44b1e33bd6419daf3baeaabeba16b4027f0c82faaff6bff3981cf5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c923dc28ed461b81462e6981e040ea9b0595b674070c2fe3606cc0ae881925)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1109b2144c95784468091e1b248eef32c39057a1eabde563b8e7b5ef35a5e18)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c10634e978833a74ac6a2a5970bf8d2df4251724a74bfbc90823d8a242d2545d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4580c328fea6d53c2678e60c00080cb3b76a4684d3d8c64bd13ceb2886b1b82c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dc0423dba32daa2e5044aa3eb6cdeb10191adf1fba0f18d724731397bd27fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1ff284d16eace3358f246a0393a9a47ca44b2f98fc069cfa1446ffdc6bbc639)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b9a093a9ef72a1a849800c8b85596224fce87e1dc2ad166e58c9a56b22f39da)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.
        '''
        value = WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f5e00a8808a59468e2656bd834d5ae4caf58e44fff1a5087870402d447dd759b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c162eff5cf329a8c7ec32c1444b8e34987800bf496bd29c745f26a3916e5aa8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__50ae2ef152f0e9403b28b9ff9041db87f9da71233d64a0bfdab84063656fe03c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b31cd89290fe32bee41256209327662de43a94b2a1b0eb057f95eb999fadc91f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2BooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2BooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ef9d2f5c795580f5c8696d404c6022f264e7799651acdf4d5c660f8a2e57952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2BooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2BooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2BooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__49547c144d8a1b63697fddb1602740d1e4172c57791d5a719c995047202a2382)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc2b1dab61c35a829587748b4a4630dc31c099ec312f274b3644c7fc1c21d7ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2BooleanVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2BooleanVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2BooleanVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba3a40345db17a4101041f592918086ea340e648b38356db0c897686f5198be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2Config",
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
class WorkspaceSettingV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
        automatic_cluster_update_workspace: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
        boolean_val: typing.Optional[typing.Union[WorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
        default_data_security_mode: typing.Optional[typing.Union["WorkspaceSettingV2DefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_automatic_cluster_update_workspace: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_default_data_security_mode: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveDefaultDataSecurityMode", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_personal_compute: typing.Optional[typing.Union["WorkspaceSettingV2EffectivePersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        effective_restrict_workspace_admins: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        integer_val: typing.Optional[typing.Union["WorkspaceSettingV2IntegerVal", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        personal_compute: typing.Optional[typing.Union["WorkspaceSettingV2PersonalCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_workspace_admins: typing.Optional[typing.Union["WorkspaceSettingV2RestrictWorkspaceAdmins", typing.Dict[builtins.str, typing.Any]]] = None,
        string_val: typing.Optional[typing.Union["WorkspaceSettingV2StringVal", typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_access_policy WorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.
        :param aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.
        :param automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#automatic_cluster_update_workspace WorkspaceSettingV2#automatic_cluster_update_workspace}.
        :param boolean_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#boolean_val WorkspaceSettingV2#boolean_val}.
        :param default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#default_data_security_mode WorkspaceSettingV2#default_data_security_mode}.
        :param effective_aibi_dashboard_embedding_access_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy WorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.
        :param effective_aibi_dashboard_embedding_approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.
        :param effective_automatic_cluster_update_workspace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_automatic_cluster_update_workspace WorkspaceSettingV2#effective_automatic_cluster_update_workspace}.
        :param effective_default_data_security_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_default_data_security_mode WorkspaceSettingV2#effective_default_data_security_mode}.
        :param effective_personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_personal_compute WorkspaceSettingV2#effective_personal_compute}.
        :param effective_restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_restrict_workspace_admins WorkspaceSettingV2#effective_restrict_workspace_admins}.
        :param integer_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#integer_val WorkspaceSettingV2#integer_val}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#name WorkspaceSettingV2#name}.
        :param personal_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#personal_compute WorkspaceSettingV2#personal_compute}.
        :param restrict_workspace_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restrict_workspace_admins WorkspaceSettingV2#restrict_workspace_admins}.
        :param string_val: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#string_val WorkspaceSettingV2#string_val}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#workspace_id WorkspaceSettingV2#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aibi_dashboard_embedding_access_policy, dict):
            aibi_dashboard_embedding_access_policy = WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy(**aibi_dashboard_embedding_access_policy)
        if isinstance(aibi_dashboard_embedding_approved_domains, dict):
            aibi_dashboard_embedding_approved_domains = WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains(**aibi_dashboard_embedding_approved_domains)
        if isinstance(automatic_cluster_update_workspace, dict):
            automatic_cluster_update_workspace = WorkspaceSettingV2AutomaticClusterUpdateWorkspace(**automatic_cluster_update_workspace)
        if isinstance(boolean_val, dict):
            boolean_val = WorkspaceSettingV2BooleanVal(**boolean_val)
        if isinstance(default_data_security_mode, dict):
            default_data_security_mode = WorkspaceSettingV2DefaultDataSecurityMode(**default_data_security_mode)
        if isinstance(effective_aibi_dashboard_embedding_access_policy, dict):
            effective_aibi_dashboard_embedding_access_policy = WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(**effective_aibi_dashboard_embedding_access_policy)
        if isinstance(effective_aibi_dashboard_embedding_approved_domains, dict):
            effective_aibi_dashboard_embedding_approved_domains = WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(**effective_aibi_dashboard_embedding_approved_domains)
        if isinstance(effective_automatic_cluster_update_workspace, dict):
            effective_automatic_cluster_update_workspace = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(**effective_automatic_cluster_update_workspace)
        if isinstance(effective_default_data_security_mode, dict):
            effective_default_data_security_mode = WorkspaceSettingV2EffectiveDefaultDataSecurityMode(**effective_default_data_security_mode)
        if isinstance(effective_personal_compute, dict):
            effective_personal_compute = WorkspaceSettingV2EffectivePersonalCompute(**effective_personal_compute)
        if isinstance(effective_restrict_workspace_admins, dict):
            effective_restrict_workspace_admins = WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(**effective_restrict_workspace_admins)
        if isinstance(integer_val, dict):
            integer_val = WorkspaceSettingV2IntegerVal(**integer_val)
        if isinstance(personal_compute, dict):
            personal_compute = WorkspaceSettingV2PersonalCompute(**personal_compute)
        if isinstance(restrict_workspace_admins, dict):
            restrict_workspace_admins = WorkspaceSettingV2RestrictWorkspaceAdmins(**restrict_workspace_admins)
        if isinstance(string_val, dict):
            string_val = WorkspaceSettingV2StringVal(**string_val)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e50eef81b76c2cb491dc39d174411b634a3fdda81a466ceec7a655a94d10f48d)
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
    ) -> typing.Optional[WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_access_policy WorkspaceSettingV2#aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional[WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy], result)

    @builtins.property
    def aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional[WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional[WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains], result)

    @builtins.property
    def automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional[WorkspaceSettingV2AutomaticClusterUpdateWorkspace]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#automatic_cluster_update_workspace WorkspaceSettingV2#automatic_cluster_update_workspace}.'''
        result = self._values.get("automatic_cluster_update_workspace")
        return typing.cast(typing.Optional[WorkspaceSettingV2AutomaticClusterUpdateWorkspace], result)

    @builtins.property
    def boolean_val(self) -> typing.Optional[WorkspaceSettingV2BooleanVal]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#boolean_val WorkspaceSettingV2#boolean_val}.'''
        result = self._values.get("boolean_val")
        return typing.cast(typing.Optional[WorkspaceSettingV2BooleanVal], result)

    @builtins.property
    def default_data_security_mode(
        self,
    ) -> typing.Optional["WorkspaceSettingV2DefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#default_data_security_mode WorkspaceSettingV2#default_data_security_mode}.'''
        result = self._values.get("default_data_security_mode")
        return typing.cast(typing.Optional["WorkspaceSettingV2DefaultDataSecurityMode"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_access_policy(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_access_policy WorkspaceSettingV2#effective_aibi_dashboard_embedding_access_policy}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_access_policy")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy"], result)

    @builtins.property
    def effective_aibi_dashboard_embedding_approved_domains(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_aibi_dashboard_embedding_approved_domains WorkspaceSettingV2#effective_aibi_dashboard_embedding_approved_domains}.'''
        result = self._values.get("effective_aibi_dashboard_embedding_approved_domains")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains"], result)

    @builtins.property
    def effective_automatic_cluster_update_workspace(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_automatic_cluster_update_workspace WorkspaceSettingV2#effective_automatic_cluster_update_workspace}.'''
        result = self._values.get("effective_automatic_cluster_update_workspace")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace"], result)

    @builtins.property
    def effective_default_data_security_mode(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveDefaultDataSecurityMode"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_default_data_security_mode WorkspaceSettingV2#effective_default_data_security_mode}.'''
        result = self._values.get("effective_default_data_security_mode")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveDefaultDataSecurityMode"], result)

    @builtins.property
    def effective_personal_compute(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectivePersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_personal_compute WorkspaceSettingV2#effective_personal_compute}.'''
        result = self._values.get("effective_personal_compute")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectivePersonalCompute"], result)

    @builtins.property
    def effective_restrict_workspace_admins(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#effective_restrict_workspace_admins WorkspaceSettingV2#effective_restrict_workspace_admins}.'''
        result = self._values.get("effective_restrict_workspace_admins")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins"], result)

    @builtins.property
    def integer_val(self) -> typing.Optional["WorkspaceSettingV2IntegerVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#integer_val WorkspaceSettingV2#integer_val}.'''
        result = self._values.get("integer_val")
        return typing.cast(typing.Optional["WorkspaceSettingV2IntegerVal"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#name WorkspaceSettingV2#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personal_compute(self) -> typing.Optional["WorkspaceSettingV2PersonalCompute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#personal_compute WorkspaceSettingV2#personal_compute}.'''
        result = self._values.get("personal_compute")
        return typing.cast(typing.Optional["WorkspaceSettingV2PersonalCompute"], result)

    @builtins.property
    def restrict_workspace_admins(
        self,
    ) -> typing.Optional["WorkspaceSettingV2RestrictWorkspaceAdmins"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restrict_workspace_admins WorkspaceSettingV2#restrict_workspace_admins}.'''
        result = self._values.get("restrict_workspace_admins")
        return typing.cast(typing.Optional["WorkspaceSettingV2RestrictWorkspaceAdmins"], result)

    @builtins.property
    def string_val(self) -> typing.Optional["WorkspaceSettingV2StringVal"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#string_val WorkspaceSettingV2#string_val}.'''
        result = self._values.get("string_val")
        return typing.cast(typing.Optional["WorkspaceSettingV2StringVal"], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#workspace_id WorkspaceSettingV2#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2DefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class WorkspaceSettingV2DefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71f84e601c598c8c54259fc47c6b561c05bd397deaaf8fd7017e17bed4435312)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2DefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2DefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2DefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf6eceb571fa57ba14060b5e4df069ab89e41b3b99151a9472b2e972c50bb619)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da55e89f1873c6106d12996419993f78fdd048d757f81cc7c1877ba46e61372c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2DefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2DefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2DefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d834d5f4923ee6442edbeb691b3b91d2b972e72e5ec49ec27bada1972d45e128)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    jsii_struct_bases=[],
    name_mapping={"access_policy_type": "accessPolicyType"},
)
class WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy:
    def __init__(self, *, access_policy_type: builtins.str) -> None:
        '''
        :param access_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d472eacc283465fee9f15ed8744945700f8adff3222b3d57b520f82f4b070ce4)
            check_type(argname="argument access_policy_type", value=access_policy_type, expected_type=type_hints["access_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policy_type": access_policy_type,
        }

    @builtins.property
    def access_policy_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#access_policy_type WorkspaceSettingV2#access_policy_type}.'''
        result = self._values.get("access_policy_type")
        assert result is not None, "Required property 'access_policy_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__467de298e2ae2072746736777d74f58cb00f92f59115d7fa33897f6ba85bcd54)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de7c2f95ccd3851aee6dd7fa6ba40f00ac09575987f5a7a300d5c1857f91ef2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__758c9300baa9344ea7b120afb7af96af92e378dd22f37eec5160501af1a70e57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    jsii_struct_bases=[],
    name_mapping={"approved_domains": "approvedDomains"},
)
class WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains:
    def __init__(
        self,
        *,
        approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a97d36c9a3349adf1381dc716ac6dd8d88a7d4770823b69111303320f7402456)
            check_type(argname="argument approved_domains", value=approved_domains, expected_type=type_hints["approved_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if approved_domains is not None:
            self._values["approved_domains"] = approved_domains

    @builtins.property
    def approved_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#approved_domains WorkspaceSettingV2#approved_domains}.'''
        result = self._values.get("approved_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__078ca8a4b1541ab101e504f015e86319e4cec9d8513a4c8243405e16d898fa11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__496041517355984e9527040dc807f8cb57bc0314b26248ab0a650aa3462f2771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "approvedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d1e1b9288c799f2dad5e77677a161de146afe9ff2ae2153848570d7e2240eed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    jsii_struct_bases=[],
    name_mapping={
        "can_toggle": "canToggle",
        "enabled": "enabled",
        "enablement_details": "enablementDetails",
        "maintenance_window": "maintenanceWindow",
        "restart_even_if_no_updates_available": "restartEvenIfNoUpdatesAvailable",
    },
)
class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace:
    def __init__(
        self,
        *,
        can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enablement_details: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        maintenance_window: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param can_toggle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.
        :param enablement_details: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.
        :param restart_even_if_no_updates_available: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.
        '''
        if isinstance(enablement_details, dict):
            enablement_details = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(**enablement_details)
        if isinstance(maintenance_window, dict):
            maintenance_window = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(**maintenance_window)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad1ed85b9c960c69a47b015d3146fbd4e648567a9413b86752131073455e8318)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#can_toggle WorkspaceSettingV2#can_toggle}.'''
        result = self._values.get("can_toggle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enabled WorkspaceSettingV2#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enablement_details(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#enablement_details WorkspaceSettingV2#enablement_details}.'''
        result = self._values.get("enablement_details")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails"], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#maintenance_window WorkspaceSettingV2#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow"], result)

    @builtins.property
    def restart_even_if_no_updates_available(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#restart_even_if_no_updates_available WorkspaceSettingV2#restart_even_if_no_updates_available}.'''
        result = self._values.get("restart_even_if_no_updates_available")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    jsii_struct_bases=[],
    name_mapping={
        "forced_for_compliance_mode": "forcedForComplianceMode",
        "unavailable_for_disabled_entitlement": "unavailableForDisabledEntitlement",
        "unavailable_for_non_enterprise_tier": "unavailableForNonEnterpriseTier",
    },
)
class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails:
    def __init__(
        self,
        *,
        forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ef21a8f86a89a3e0a94a15c3038e2c2429b93c5a2a97a88654c5ce778b6bbc2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.'''
        result = self._values.get("forced_for_compliance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_disabled_entitlement(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.'''
        result = self._values.get("unavailable_for_disabled_entitlement")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unavailable_for_non_enterprise_tier(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.'''
        result = self._values.get("unavailable_for_non_enterprise_tier")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e95fd7c80ed99d774c184098667d663eac2c0a5dd2754838d117fb3b06a11c23)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47f5aaa6d12e8a79eedb79bf9a3faaa1a75d319c7fcc8d0b36574170b470fce1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd76fdf9196cb380e72516882be36d49922871d916cf31937ad05f15f3cc73b2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6512494555b7169f2fedbe3207a871b63bdddad6c2a2e62425ea1f6022415d38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unavailableForNonEnterpriseTier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418ab823bd46f471a622a471498f2365dc909d130fa7a8707f7ad383b9245a63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"week_day_based_schedule": "weekDayBasedSchedule"},
)
class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow:
    def __init__(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.
        '''
        if isinstance(week_day_based_schedule, dict):
            week_day_based_schedule = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(**week_day_based_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fdbc390d61c46f42ed9ce4ee275dc850badcfa664c3ed43df8ea180f2a34a9a)
            check_type(argname="argument week_day_based_schedule", value=week_day_based_schedule, expected_type=type_hints["week_day_based_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if week_day_based_schedule is not None:
            self._values["week_day_based_schedule"] = week_day_based_schedule

    @builtins.property
    def week_day_based_schedule(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.'''
        result = self._values.get("week_day_based_schedule")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb8b4dd0c546fa66cd35e57fd0801cf60379af280477a11418bd2b2a660eb7f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWeekDayBasedSchedule")
    def put_week_day_based_schedule(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.
        '''
        value = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(
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
    ) -> "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference", jsii.get(self, "weekDayBasedSchedule"))

    @builtins.property
    @jsii.member(jsii_name="weekDayBasedScheduleInput")
    def week_day_based_schedule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule"]], jsii.get(self, "weekDayBasedScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec0642749d4435603c52155182e516b3db27bb87fecb9658836f1f70f00e1573)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "window_start_time": "windowStartTime",
    },
)
class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule:
    def __init__(
        self,
        *,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        window_start_time: typing.Optional[typing.Union["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.
        :param window_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.
        '''
        if isinstance(window_start_time, dict):
            window_start_time = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(**window_start_time)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f50d647d73e5e61ffa303ad208bc27a727dd9c7e4f9109eb264d9ef81581f965)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#day_of_week WorkspaceSettingV2#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#frequency WorkspaceSettingV2#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def window_start_time(
        self,
    ) -> typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#window_start_time WorkspaceSettingV2#window_start_time}.'''
        result = self._values.get("window_start_time")
        return typing.cast(typing.Optional["WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ab91e378a5c9831fad0e243b07e3dd6a0cce6bdebe72e15aa852139cf221716)
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
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.
        '''
        value = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(
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
    ) -> "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference":
        return typing.cast("WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference", jsii.get(self, "windowStartTime"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime"]], jsii.get(self, "windowStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b866298aa5136c5adb78e04b7fdc5b557db5bd46c94509b49a0a95adb6b6f28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3c2115fc171cb9fd8e2463cbebe8b26fc21ac2d0caaf379db0e55506bbae1c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47931598fc00e0009b0ff27318211749382d16ee9e2c8bea3b936205dd2f0da3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    jsii_struct_bases=[],
    name_mapping={"hours": "hours", "minutes": "minutes"},
)
class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime:
    def __init__(
        self,
        *,
        hours: typing.Optional[jsii.Number] = None,
        minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.
        :param minutes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03ca1af6b8687f92ab141376f3be1e729a119fd1238398b77b54c64013e29a0b)
            check_type(argname="argument hours", value=hours, expected_type=type_hints["hours"])
            check_type(argname="argument minutes", value=minutes, expected_type=type_hints["minutes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hours is not None:
            self._values["hours"] = hours
        if minutes is not None:
            self._values["minutes"] = minutes

    @builtins.property
    def hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#hours WorkspaceSettingV2#hours}.'''
        result = self._values.get("hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#minutes WorkspaceSettingV2#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee26ccf9c7ff286450b3db577f5353c9559ee8966462ef0f7dd0fdc4f94b1c47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b501f47d22c5c8d3228062806d15e4a627261c6e48df8b69cf3ace7894b08310)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d05a331fa7ac3e6bb828d8d0741e18fe3496dae8e29cf743e3491502a4f5b14b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b3292316ec553cc58ddd51301bddfe854da858ef15c8018d14a62826ac506c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f74fbc5fce8c024082f8c148b74f6c03e0fda17b47cda2f79115af36d31aea15)
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
        :param forced_for_compliance_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#forced_for_compliance_mode WorkspaceSettingV2#forced_for_compliance_mode}.
        :param unavailable_for_disabled_entitlement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_disabled_entitlement WorkspaceSettingV2#unavailable_for_disabled_entitlement}.
        :param unavailable_for_non_enterprise_tier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#unavailable_for_non_enterprise_tier WorkspaceSettingV2#unavailable_for_non_enterprise_tier}.
        '''
        value = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails(
            forced_for_compliance_mode=forced_for_compliance_mode,
            unavailable_for_disabled_entitlement=unavailable_for_disabled_entitlement,
            unavailable_for_non_enterprise_tier=unavailable_for_non_enterprise_tier,
        )

        return typing.cast(None, jsii.invoke(self, "putEnablementDetails", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        week_day_based_schedule: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param week_day_based_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#week_day_based_schedule WorkspaceSettingV2#week_day_based_schedule}.
        '''
        value = WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow(
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
    ) -> WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference:
        return typing.cast(WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference, jsii.get(self, "enablementDetails"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference:
        return typing.cast(WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference, jsii.get(self, "maintenanceWindow"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]], jsii.get(self, "enablementDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]], jsii.get(self, "maintenanceWindowInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__d07db28b6c73f48d0401469b07cfa2245ea6f35f77ed2e20a25a38a61ba3b891)
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
            type_hints = typing.get_type_hints(_typecheckingstub__35aef55468e0a85b0ec20f636d3ac9076d6db6aedaebc1352968087e2663ac6c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__318a7f4f7e04aa4e574a894ece4bee78d7edc775b0b72cd5e318b07d092a4909)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartEvenIfNoUpdatesAvailable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__480722e2dcbeefbe8243025400dc02b12d54b3784b36c15a1b065acd150a4704)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveBooleanVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2EffectiveBooleanVal:
    def __init__(
        self,
        *,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9b13ae8ffa0483dcb2dc9cc8df83fa4da33419876f8be5b43838f96a630c22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveBooleanVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveBooleanValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveBooleanValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__836993fe79d084dc8409ebe4c81db3df7632119f3d2d4eb000bbab87f02cb938)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5cbca6ade8e4c204ce083cc8eb726d8ffa18c8cecdf84c3da615356333ff12f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkspaceSettingV2EffectiveBooleanVal]:
        return typing.cast(typing.Optional[WorkspaceSettingV2EffectiveBooleanVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspaceSettingV2EffectiveBooleanVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e297fdf1cb6a48998fc6567cc3b87cada2f207e3df110f571af4d873e6390f94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveDefaultDataSecurityMode",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class WorkspaceSettingV2EffectiveDefaultDataSecurityMode:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794a03d6742fa5ddbc6085a9cd00b74f7fe5b6a65da1fbdd376502bada81fcd5)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveDefaultDataSecurityMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd627865a42dd24bdc683e38db4f87d5ab6a23036437dab198576578cc964969)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f1b9b583652758de29637b420c083c3653259901f2f999ae3d8456ca97709d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveDefaultDataSecurityMode]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveDefaultDataSecurityMode]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveDefaultDataSecurityMode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74aaea3e34e16c9bb10710c7d01d2ccd0125b77f1cb37d89e95e1f52cd884d2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveIntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2EffectiveIntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da87819b79772b3b5b5f2985851ec59da9da4fec612b4b313919568105c5c855)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveIntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveIntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveIntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a976a3bea36ed6e4d4a2cbd15520a535d759849928b52481b67f346861235a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2716c692fb4ffe008e5003cfc1288496e82bf82483c53d5911b7c13f3cdbcd66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkspaceSettingV2EffectiveIntegerVal]:
        return typing.cast(typing.Optional[WorkspaceSettingV2EffectiveIntegerVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspaceSettingV2EffectiveIntegerVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f118cd94b807bb1ece8ec19990d2e8fce9879719cc33c05b4844bff2f98636a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectivePersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2EffectivePersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__018d3399eaa4865a1da3b00d98d7082fce4b05e722a592e3c18ef751e5bf802c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectivePersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectivePersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectivePersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ae06057047e387e679c9d0e238d5f13b8cf1adb8fcd870f819daefa7fca84bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c08e0fd5132316696929085124a3f08c6a3d990a403879f91c1fb752a3bc768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectivePersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectivePersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectivePersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b45c6cad5d5ef20136db4f77e9cba88ad4f0c9166149b956ec402443c28df1d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba9bded02d4014d10f519073353e4645b5a00fcbd6799cad92f8fdbfd41b745)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6ac0d96a513821b484269bdb2ab4dae496beabb982dd95a0c7f664bc1d166f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__214b0c1991527e80c419631a8aa35ad1e0557756f44517022c8371e596a0ce32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97a4a97c48ab2dbb0dcdeb6d5546e952e89927ee9071a2b462f61be6561f4c22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveStringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2EffectiveStringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01e9ff6282ae63b7cda293a4e2725e7f0011fd24bbd8351e6c3e20456059099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2EffectiveStringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2EffectiveStringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2EffectiveStringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95a19222650001aa6646bf65415e059ae248e6a0ffb4496de396e5c496513833)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9dbf311f21acbcae7314d2616a14e4d5e121a779af8071c0d74863f7deedb29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkspaceSettingV2EffectiveStringVal]:
        return typing.cast(typing.Optional[WorkspaceSettingV2EffectiveStringVal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspaceSettingV2EffectiveStringVal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e909c93816ece6aaa191bd4934579ab52b5db404065611ece28ea70b5414b6d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2IntegerVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2IntegerVal:
    def __init__(self, *, value: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a1a84a6870db00d09683b39de26562994d17c1ed8cbfd0fa9e49d38c6d10f8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2IntegerVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2IntegerValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2IntegerValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d9676fe4c3740e11cacb03ad5d9b3900ec69881d963ff8e44ea8f2a45b815d5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__53a83804442103468ab408bdcbf6083f77def3c459cd3b2305c53b2dd06d5973)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2IntegerVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2IntegerVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2IntegerVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26cecc4e519b423af391f8f6289c95c2305937a0a3f35c361e54193428e408c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2PersonalCompute",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2PersonalCompute:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d85c3bb42c7ea8756150181c4575e0058ea45b9881a119997627926e93a3b66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2PersonalCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2PersonalComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2PersonalComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__87d067e12c2abfeaf9b0936e9d15c3355993c48d2a8bdc70f6184b33e30fd679)
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
            type_hints = typing.get_type_hints(_typecheckingstub__23ca909b5630c0c1abb962c243bfe4ec3e29444728543da60a561d35f4e3c830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2PersonalCompute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2PersonalCompute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2PersonalCompute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8a6eabec08542ac6d1a1268f2ae285ed0958ec79841d27f068342b919dd8bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2RestrictWorkspaceAdmins",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class WorkspaceSettingV2RestrictWorkspaceAdmins:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73a5ebe28bba65c170824fcf0b6a47ac465e40caba936cc312b8a7c629eeeb5e)
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#status WorkspaceSettingV2#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2RestrictWorkspaceAdmins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2RestrictWorkspaceAdminsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2RestrictWorkspaceAdminsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8acbd39a8c3623407dec1fc96012f02dffcc1ceb1c7853152d0348ac0b7870c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5d15a4c58c0bf1d6b0f2cc1a1e5ec7a22f8e7e1b1e1dc5911a2472c658bdea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2RestrictWorkspaceAdmins]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2RestrictWorkspaceAdmins]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2RestrictWorkspaceAdmins]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f69267ff8463a67965ecaf25328d68f36d0eea3fbd0021d66fa02107a323bbc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2StringVal",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class WorkspaceSettingV2StringVal:
    def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
        '''
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b813aed795099ce71d3e60602b623e5ff2c712eb3603550e43a105cb2a7cae4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/workspace_setting_v2#value WorkspaceSettingV2#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingV2StringVal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingV2StringValOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.workspaceSettingV2.WorkspaceSettingV2StringValOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e588ef6e36e6a37482fee63279484f8fce08c4368095975e7b5f3f8ccd52354)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0b64978c7f53e3803072f2ade4f29804a53d2df49b6ecdfc485678c14ac9c8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2StringVal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2StringVal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2StringVal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7485a4ea535dfb1d3479bb1cea815b3379be1e6eacfe33842e99463598d1466f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "WorkspaceSettingV2",
    "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy",
    "WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicyOutputReference",
    "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains",
    "WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomainsOutputReference",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspace",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "WorkspaceSettingV2AutomaticClusterUpdateWorkspaceOutputReference",
    "WorkspaceSettingV2BooleanVal",
    "WorkspaceSettingV2BooleanValOutputReference",
    "WorkspaceSettingV2Config",
    "WorkspaceSettingV2DefaultDataSecurityMode",
    "WorkspaceSettingV2DefaultDataSecurityModeOutputReference",
    "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy",
    "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicyOutputReference",
    "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains",
    "WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomainsOutputReference",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetailsOutputReference",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowOutputReference",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleOutputReference",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTimeOutputReference",
    "WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceOutputReference",
    "WorkspaceSettingV2EffectiveBooleanVal",
    "WorkspaceSettingV2EffectiveBooleanValOutputReference",
    "WorkspaceSettingV2EffectiveDefaultDataSecurityMode",
    "WorkspaceSettingV2EffectiveDefaultDataSecurityModeOutputReference",
    "WorkspaceSettingV2EffectiveIntegerVal",
    "WorkspaceSettingV2EffectiveIntegerValOutputReference",
    "WorkspaceSettingV2EffectivePersonalCompute",
    "WorkspaceSettingV2EffectivePersonalComputeOutputReference",
    "WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins",
    "WorkspaceSettingV2EffectiveRestrictWorkspaceAdminsOutputReference",
    "WorkspaceSettingV2EffectiveStringVal",
    "WorkspaceSettingV2EffectiveStringValOutputReference",
    "WorkspaceSettingV2IntegerVal",
    "WorkspaceSettingV2IntegerValOutputReference",
    "WorkspaceSettingV2PersonalCompute",
    "WorkspaceSettingV2PersonalComputeOutputReference",
    "WorkspaceSettingV2RestrictWorkspaceAdmins",
    "WorkspaceSettingV2RestrictWorkspaceAdminsOutputReference",
    "WorkspaceSettingV2StringVal",
    "WorkspaceSettingV2StringValOutputReference",
]

publication.publish()

def _typecheckingstub__f267c4ea4afb3ee8b2f333d2f369563745a9d40b819a9c3ee6943fc5661a6c2c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[WorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[WorkspaceSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[WorkspaceSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[WorkspaceSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[WorkspaceSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[WorkspaceSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[WorkspaceSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__e38844a0504ea424c5942d3fe81c158def1c3d1025a993e8658e1cc8d04e823b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b504a46d417967fd0e842f4df21c8d3b5728cbe2886e3b9b82f5721c0004c050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da970c4a98bbfbb138a79343d967aadbaa8e3a58b17a0d946e88c8c64abd9873(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7d3498e7e42a46ce17411ad2257a8dfcc7b4a9d5e63cbcbb81417076a62707(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85afabce50ea404b9bee9057fac3e04a6142077dcc93240bb31421cdb5c6de88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a718ee456f778df5d388faa81c61230f6addd1b2c494b806edfeb396f450ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cafeff69ee98d9ad30919416883511c67b54f21b7ade83e172ca1db7fa27c0e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e904ae13b024580fefd5b554aab0abe4436b145f99e0270d638b33ffa25d4e9f(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687c11bfca12ae94a8ad7a503f9ef98c38fefe741a2fd4d275c3a62e723cb972(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7849e7134eaf63d7fca98164dd5aa3a3cd6185b809dbf096e7262dd0a99001(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3c53c08e1ff0d131af6b2e00146b1655782e63bf74622c612c36a5a87c1cc32(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692c0551b5180577ed48d5b302c0590a6fa5ffacffa7a4c0c34063fe69940914(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c968c0ca28a18853263c08ecc0f59c92ebd99c7e87d0bc4cb30205549df8fd48(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d61723d20fbec84d160c6154327d7cdc50e7dbc9af01c705f069e666e82f76e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8504d9b01b6747de1df9900505792c81e1f84e679ee9d1c3a2a337c50e5baf1d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a0c57bad1b610d3868ba98c411b921932991f9ea4ec24fbc80dcf30d6f37d35(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__862c3e35beacd440d0c0dded98b4d8aaace7d767d0aa7a82beca18e754ea927c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da2be8d34f7ecad0d5992bffe6ff8e4ad3146fcc753fc6e3f916fe1a2ca752a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__634cfb55242b35f404abfc640248b2cacbfe7cdba7b6674e6df77c4694df318a(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab113f15e4fffdb42794d555f12c842ac3afa92ef22a4c1e7687e635339b97a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1994eda3c9c0a63459da88a744ff338c6c24ea4460903c6adb0f8ec834506c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955f6d4eb41c930a9b9ee5bbe61f4b80c31e62320d0c2a441f7b185d1d6b93c0(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40920a97f7e4e6d9b908171044582c6ff6cb617e48e89277e1341ee73be99733(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a6f22a7ef4dfbee17b4905d07289d3378f420cba8109341ea21315934e92e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae2b243a44b1e33bd6419daf3baeaabeba16b4027f0c82faaff6bff3981cf5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c923dc28ed461b81462e6981e040ea9b0595b674070c2fe3606cc0ae881925(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1109b2144c95784468091e1b248eef32c39057a1eabde563b8e7b5ef35a5e18(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c10634e978833a74ac6a2a5970bf8d2df4251724a74bfbc90823d8a242d2545d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4580c328fea6d53c2678e60c00080cb3b76a4684d3d8c64bd13ceb2886b1b82c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dc0423dba32daa2e5044aa3eb6cdeb10191adf1fba0f18d724731397bd27fad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1ff284d16eace3358f246a0393a9a47ca44b2f98fc069cfa1446ffdc6bbc639(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b9a093a9ef72a1a849800c8b85596224fce87e1dc2ad166e58c9a56b22f39da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5e00a8808a59468e2656bd834d5ae4caf58e44fff1a5087870402d447dd759b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c162eff5cf329a8c7ec32c1444b8e34987800bf496bd29c745f26a3916e5aa8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50ae2ef152f0e9403b28b9ff9041db87f9da71233d64a0bfdab84063656fe03c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b31cd89290fe32bee41256209327662de43a94b2a1b0eb057f95eb999fadc91f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2AutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ef9d2f5c795580f5c8696d404c6022f264e7799651acdf4d5c660f8a2e57952(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49547c144d8a1b63697fddb1602740d1e4172c57791d5a719c995047202a2382(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2b1dab61c35a829587748b4a4630dc31c099ec312f274b3644c7fc1c21d7ce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba3a40345db17a4101041f592918086ea340e648b38356db0c897686f5198be(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2BooleanVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e50eef81b76c2cb491dc39d174411b634a3fdda81a466ceec7a655a94d10f48d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[WorkspaceSettingV2AibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    automatic_cluster_update_workspace: typing.Optional[typing.Union[WorkspaceSettingV2AutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    boolean_val: typing.Optional[typing.Union[WorkspaceSettingV2BooleanVal, typing.Dict[builtins.str, typing.Any]]] = None,
    default_data_security_mode: typing.Optional[typing.Union[WorkspaceSettingV2DefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_access_policy: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_aibi_dashboard_embedding_approved_domains: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_automatic_cluster_update_workspace: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_default_data_security_mode: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveDefaultDataSecurityMode, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_personal_compute: typing.Optional[typing.Union[WorkspaceSettingV2EffectivePersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    effective_restrict_workspace_admins: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    integer_val: typing.Optional[typing.Union[WorkspaceSettingV2IntegerVal, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    personal_compute: typing.Optional[typing.Union[WorkspaceSettingV2PersonalCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_workspace_admins: typing.Optional[typing.Union[WorkspaceSettingV2RestrictWorkspaceAdmins, typing.Dict[builtins.str, typing.Any]]] = None,
    string_val: typing.Optional[typing.Union[WorkspaceSettingV2StringVal, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f84e601c598c8c54259fc47c6b561c05bd397deaaf8fd7017e17bed4435312(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf6eceb571fa57ba14060b5e4df069ab89e41b3b99151a9472b2e972c50bb619(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da55e89f1873c6106d12996419993f78fdd048d757f81cc7c1877ba46e61372c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d834d5f4923ee6442edbeb691b3b91d2b972e72e5ec49ec27bada1972d45e128(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2DefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d472eacc283465fee9f15ed8744945700f8adff3222b3d57b520f82f4b070ce4(
    *,
    access_policy_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467de298e2ae2072746736777d74f58cb00f92f59115d7fa33897f6ba85bcd54(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7c2f95ccd3851aee6dd7fa6ba40f00ac09575987f5a7a300d5c1857f91ef2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758c9300baa9344ea7b120afb7af96af92e378dd22f37eec5160501af1a70e57(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingAccessPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a97d36c9a3349adf1381dc716ac6dd8d88a7d4770823b69111303320f7402456(
    *,
    approved_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078ca8a4b1541ab101e504f015e86319e4cec9d8513a4c8243405e16d898fa11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__496041517355984e9527040dc807f8cb57bc0314b26248ab0a650aa3462f2771(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d1e1b9288c799f2dad5e77677a161de146afe9ff2ae2153848570d7e2240eed(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAibiDashboardEmbeddingApprovedDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1ed85b9c960c69a47b015d3146fbd4e648567a9413b86752131073455e8318(
    *,
    can_toggle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enablement_details: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    maintenance_window: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    restart_even_if_no_updates_available: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef21a8f86a89a3e0a94a15c3038e2c2429b93c5a2a97a88654c5ce778b6bbc2(
    *,
    forced_for_compliance_mode: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_disabled_entitlement: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unavailable_for_non_enterprise_tier: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95fd7c80ed99d774c184098667d663eac2c0a5dd2754838d117fb3b06a11c23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f5aaa6d12e8a79eedb79bf9a3faaa1a75d319c7fcc8d0b36574170b470fce1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd76fdf9196cb380e72516882be36d49922871d916cf31937ad05f15f3cc73b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6512494555b7169f2fedbe3207a871b63bdddad6c2a2e62425ea1f6022415d38(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418ab823bd46f471a622a471498f2365dc909d130fa7a8707f7ad383b9245a63(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceEnablementDetails]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fdbc390d61c46f42ed9ce4ee275dc850badcfa664c3ed43df8ea180f2a34a9a(
    *,
    week_day_based_schedule: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8b4dd0c546fa66cd35e57fd0801cf60379af280477a11418bd2b2a660eb7f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec0642749d4435603c52155182e516b3db27bb87fecb9658836f1f70f00e1573(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindow]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f50d647d73e5e61ffa303ad208bc27a727dd9c7e4f9109eb264d9ef81581f965(
    *,
    day_of_week: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    window_start_time: typing.Optional[typing.Union[WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab91e378a5c9831fad0e243b07e3dd6a0cce6bdebe72e15aa852139cf221716(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b866298aa5136c5adb78e04b7fdc5b557db5bd46c94509b49a0a95adb6b6f28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3c2115fc171cb9fd8e2463cbebe8b26fc21ac2d0caaf379db0e55506bbae1c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47931598fc00e0009b0ff27318211749382d16ee9e2c8bea3b936205dd2f0da3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedSchedule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03ca1af6b8687f92ab141376f3be1e729a119fd1238398b77b54c64013e29a0b(
    *,
    hours: typing.Optional[jsii.Number] = None,
    minutes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee26ccf9c7ff286450b3db577f5353c9559ee8966462ef0f7dd0fdc4f94b1c47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b501f47d22c5c8d3228062806d15e4a627261c6e48df8b69cf3ace7894b08310(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d05a331fa7ac3e6bb828d8d0741e18fe3496dae8e29cf743e3491502a4f5b14b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b3292316ec553cc58ddd51301bddfe854da858ef15c8018d14a62826ac506c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspaceMaintenanceWindowWeekDayBasedScheduleWindowStartTime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f74fbc5fce8c024082f8c148b74f6c03e0fda17b47cda2f79115af36d31aea15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d07db28b6c73f48d0401469b07cfa2245ea6f35f77ed2e20a25a38a61ba3b891(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35aef55468e0a85b0ec20f636d3ac9076d6db6aedaebc1352968087e2663ac6c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__318a7f4f7e04aa4e574a894ece4bee78d7edc775b0b72cd5e318b07d092a4909(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__480722e2dcbeefbe8243025400dc02b12d54b3784b36c15a1b065acd150a4704(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveAutomaticClusterUpdateWorkspace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9b13ae8ffa0483dcb2dc9cc8df83fa4da33419876f8be5b43838f96a630c22(
    *,
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__836993fe79d084dc8409ebe4c81db3df7632119f3d2d4eb000bbab87f02cb938(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5cbca6ade8e4c204ce083cc8eb726d8ffa18c8cecdf84c3da615356333ff12f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e297fdf1cb6a48998fc6567cc3b87cada2f207e3df110f571af4d873e6390f94(
    value: typing.Optional[WorkspaceSettingV2EffectiveBooleanVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794a03d6742fa5ddbc6085a9cd00b74f7fe5b6a65da1fbdd376502bada81fcd5(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd627865a42dd24bdc683e38db4f87d5ab6a23036437dab198576578cc964969(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1b9b583652758de29637b420c083c3653259901f2f999ae3d8456ca97709d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74aaea3e34e16c9bb10710c7d01d2ccd0125b77f1cb37d89e95e1f52cd884d2b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveDefaultDataSecurityMode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da87819b79772b3b5b5f2985851ec59da9da4fec612b4b313919568105c5c855(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a976a3bea36ed6e4d4a2cbd15520a535d759849928b52481b67f346861235a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2716c692fb4ffe008e5003cfc1288496e82bf82483c53d5911b7c13f3cdbcd66(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f118cd94b807bb1ece8ec19990d2e8fce9879719cc33c05b4844bff2f98636a(
    value: typing.Optional[WorkspaceSettingV2EffectiveIntegerVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018d3399eaa4865a1da3b00d98d7082fce4b05e722a592e3c18ef751e5bf802c(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ae06057047e387e679c9d0e238d5f13b8cf1adb8fcd870f819daefa7fca84bf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c08e0fd5132316696929085124a3f08c6a3d990a403879f91c1fb752a3bc768(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b45c6cad5d5ef20136db4f77e9cba88ad4f0c9166149b956ec402443c28df1d4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectivePersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba9bded02d4014d10f519073353e4645b5a00fcbd6799cad92f8fdbfd41b745(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ac0d96a513821b484269bdb2ab4dae496beabb982dd95a0c7f664bc1d166f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__214b0c1991527e80c419631a8aa35ad1e0557756f44517022c8371e596a0ce32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97a4a97c48ab2dbb0dcdeb6d5546e952e89927ee9071a2b462f61be6561f4c22(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2EffectiveRestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b01e9ff6282ae63b7cda293a4e2725e7f0011fd24bbd8351e6c3e20456059099(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95a19222650001aa6646bf65415e059ae248e6a0ffb4496de396e5c496513833(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9dbf311f21acbcae7314d2616a14e4d5e121a779af8071c0d74863f7deedb29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e909c93816ece6aaa191bd4934579ab52b5db404065611ece28ea70b5414b6d1(
    value: typing.Optional[WorkspaceSettingV2EffectiveStringVal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a1a84a6870db00d09683b39de26562994d17c1ed8cbfd0fa9e49d38c6d10f8f(
    *,
    value: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d9676fe4c3740e11cacb03ad5d9b3900ec69881d963ff8e44ea8f2a45b815d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a83804442103468ab408bdcbf6083f77def3c459cd3b2305c53b2dd06d5973(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26cecc4e519b423af391f8f6289c95c2305937a0a3f35c361e54193428e408c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2IntegerVal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d85c3bb42c7ea8756150181c4575e0058ea45b9881a119997627926e93a3b66(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87d067e12c2abfeaf9b0936e9d15c3355993c48d2a8bdc70f6184b33e30fd679(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23ca909b5630c0c1abb962c243bfe4ec3e29444728543da60a561d35f4e3c830(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8a6eabec08542ac6d1a1268f2ae285ed0958ec79841d27f068342b919dd8bd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2PersonalCompute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73a5ebe28bba65c170824fcf0b6a47ac465e40caba936cc312b8a7c629eeeb5e(
    *,
    status: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8acbd39a8c3623407dec1fc96012f02dffcc1ceb1c7853152d0348ac0b7870c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5d15a4c58c0bf1d6b0f2cc1a1e5ec7a22f8e7e1b1e1dc5911a2472c658bdea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f69267ff8463a67965ecaf25328d68f36d0eea3fbd0021d66fa02107a323bbc9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2RestrictWorkspaceAdmins]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b813aed795099ce71d3e60602b623e5ff2c712eb3603550e43a105cb2a7cae4(
    *,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e588ef6e36e6a37482fee63279484f8fce08c4368095975e7b5f3f8ccd52354(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b64978c7f53e3803072f2ade4f29804a53d2df49b6ecdfc485678c14ac9c8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7485a4ea535dfb1d3479bb1cea815b3379be1e6eacfe33842e99463598d1466f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, WorkspaceSettingV2StringVal]],
) -> None:
    """Type checking stubs"""
    pass
