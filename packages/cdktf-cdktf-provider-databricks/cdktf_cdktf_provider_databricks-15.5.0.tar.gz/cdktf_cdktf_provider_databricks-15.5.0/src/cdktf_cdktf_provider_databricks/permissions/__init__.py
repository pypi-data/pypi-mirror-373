r'''
# `databricks_permissions`

Refer to the Terraform Registry for docs: [`databricks_permissions`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions).
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


class Permissions(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.permissions.Permissions",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions databricks_permissions}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        access_control: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PermissionsAccessControl", typing.Dict[builtins.str, typing.Any]]]],
        alert_v2_id: typing.Optional[builtins.str] = None,
        app_name: typing.Optional[builtins.str] = None,
        authorization: typing.Optional[builtins.str] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_policy_id: typing.Optional[builtins.str] = None,
        dashboard_id: typing.Optional[builtins.str] = None,
        database_instance_name: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        directory_path: typing.Optional[builtins.str] = None,
        experiment_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        job_id: typing.Optional[builtins.str] = None,
        notebook_id: typing.Optional[builtins.str] = None,
        notebook_path: typing.Optional[builtins.str] = None,
        object_type: typing.Optional[builtins.str] = None,
        pipeline_id: typing.Optional[builtins.str] = None,
        registered_model_id: typing.Optional[builtins.str] = None,
        repo_id: typing.Optional[builtins.str] = None,
        repo_path: typing.Optional[builtins.str] = None,
        serving_endpoint_id: typing.Optional[builtins.str] = None,
        sql_alert_id: typing.Optional[builtins.str] = None,
        sql_dashboard_id: typing.Optional[builtins.str] = None,
        sql_endpoint_id: typing.Optional[builtins.str] = None,
        sql_query_id: typing.Optional[builtins.str] = None,
        vector_search_endpoint_id: typing.Optional[builtins.str] = None,
        workspace_file_id: typing.Optional[builtins.str] = None,
        workspace_file_path: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions databricks_permissions} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_control: access_control block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#access_control Permissions#access_control}
        :param alert_v2_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#alert_v2_id Permissions#alert_v2_id}.
        :param app_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#app_name Permissions#app_name}.
        :param authorization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#authorization Permissions#authorization}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_id Permissions#cluster_id}.
        :param cluster_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_policy_id Permissions#cluster_policy_id}.
        :param dashboard_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#dashboard_id Permissions#dashboard_id}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#database_instance_name Permissions#database_instance_name}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_id Permissions#directory_id}.
        :param directory_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_path Permissions#directory_path}.
        :param experiment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#experiment_id Permissions#experiment_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#id Permissions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#instance_pool_id Permissions#instance_pool_id}.
        :param job_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#job_id Permissions#job_id}.
        :param notebook_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_id Permissions#notebook_id}.
        :param notebook_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_path Permissions#notebook_path}.
        :param object_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#object_type Permissions#object_type}.
        :param pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#pipeline_id Permissions#pipeline_id}.
        :param registered_model_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#registered_model_id Permissions#registered_model_id}.
        :param repo_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_id Permissions#repo_id}.
        :param repo_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_path Permissions#repo_path}.
        :param serving_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#serving_endpoint_id Permissions#serving_endpoint_id}.
        :param sql_alert_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_alert_id Permissions#sql_alert_id}.
        :param sql_dashboard_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_dashboard_id Permissions#sql_dashboard_id}.
        :param sql_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_endpoint_id Permissions#sql_endpoint_id}.
        :param sql_query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_query_id Permissions#sql_query_id}.
        :param vector_search_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#vector_search_endpoint_id Permissions#vector_search_endpoint_id}.
        :param workspace_file_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_id Permissions#workspace_file_id}.
        :param workspace_file_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_path Permissions#workspace_file_path}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a98068f475c3ee349d67d2fb8108b3fcb806e359f2766e26580cd4d2c5e72a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PermissionsConfig(
            access_control=access_control,
            alert_v2_id=alert_v2_id,
            app_name=app_name,
            authorization=authorization,
            cluster_id=cluster_id,
            cluster_policy_id=cluster_policy_id,
            dashboard_id=dashboard_id,
            database_instance_name=database_instance_name,
            directory_id=directory_id,
            directory_path=directory_path,
            experiment_id=experiment_id,
            id=id,
            instance_pool_id=instance_pool_id,
            job_id=job_id,
            notebook_id=notebook_id,
            notebook_path=notebook_path,
            object_type=object_type,
            pipeline_id=pipeline_id,
            registered_model_id=registered_model_id,
            repo_id=repo_id,
            repo_path=repo_path,
            serving_endpoint_id=serving_endpoint_id,
            sql_alert_id=sql_alert_id,
            sql_dashboard_id=sql_dashboard_id,
            sql_endpoint_id=sql_endpoint_id,
            sql_query_id=sql_query_id,
            vector_search_endpoint_id=vector_search_endpoint_id,
            workspace_file_id=workspace_file_id,
            workspace_file_path=workspace_file_path,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a Permissions resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Permissions to import.
        :param import_from_id: The id of the existing Permissions that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Permissions to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afad0ec134fdc626669ab9a7402c28cde2875df634e69b5b0e9837a4a2dd2352)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAccessControl")
    def put_access_control(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PermissionsAccessControl", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d52cb408a8c6c421d42275c3fa76c41242be248c46b596dc95b424a836775c93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAccessControl", [value]))

    @jsii.member(jsii_name="resetAlertV2Id")
    def reset_alert_v2_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlertV2Id", []))

    @jsii.member(jsii_name="resetAppName")
    def reset_app_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppName", []))

    @jsii.member(jsii_name="resetAuthorization")
    def reset_authorization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorization", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetClusterPolicyId")
    def reset_cluster_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterPolicyId", []))

    @jsii.member(jsii_name="resetDashboardId")
    def reset_dashboard_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDashboardId", []))

    @jsii.member(jsii_name="resetDatabaseInstanceName")
    def reset_database_instance_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseInstanceName", []))

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetDirectoryPath")
    def reset_directory_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryPath", []))

    @jsii.member(jsii_name="resetExperimentId")
    def reset_experiment_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExperimentId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstancePoolId")
    def reset_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolId", []))

    @jsii.member(jsii_name="resetJobId")
    def reset_job_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobId", []))

    @jsii.member(jsii_name="resetNotebookId")
    def reset_notebook_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebookId", []))

    @jsii.member(jsii_name="resetNotebookPath")
    def reset_notebook_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebookPath", []))

    @jsii.member(jsii_name="resetObjectType")
    def reset_object_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectType", []))

    @jsii.member(jsii_name="resetPipelineId")
    def reset_pipeline_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineId", []))

    @jsii.member(jsii_name="resetRegisteredModelId")
    def reset_registered_model_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegisteredModelId", []))

    @jsii.member(jsii_name="resetRepoId")
    def reset_repo_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepoId", []))

    @jsii.member(jsii_name="resetRepoPath")
    def reset_repo_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepoPath", []))

    @jsii.member(jsii_name="resetServingEndpointId")
    def reset_serving_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServingEndpointId", []))

    @jsii.member(jsii_name="resetSqlAlertId")
    def reset_sql_alert_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlAlertId", []))

    @jsii.member(jsii_name="resetSqlDashboardId")
    def reset_sql_dashboard_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlDashboardId", []))

    @jsii.member(jsii_name="resetSqlEndpointId")
    def reset_sql_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlEndpointId", []))

    @jsii.member(jsii_name="resetSqlQueryId")
    def reset_sql_query_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlQueryId", []))

    @jsii.member(jsii_name="resetVectorSearchEndpointId")
    def reset_vector_search_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVectorSearchEndpointId", []))

    @jsii.member(jsii_name="resetWorkspaceFileId")
    def reset_workspace_file_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceFileId", []))

    @jsii.member(jsii_name="resetWorkspaceFilePath")
    def reset_workspace_file_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceFilePath", []))

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
    @jsii.member(jsii_name="accessControl")
    def access_control(self) -> "PermissionsAccessControlList":
        return typing.cast("PermissionsAccessControlList", jsii.get(self, "accessControl"))

    @builtins.property
    @jsii.member(jsii_name="accessControlInput")
    def access_control_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PermissionsAccessControl"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PermissionsAccessControl"]]], jsii.get(self, "accessControlInput"))

    @builtins.property
    @jsii.member(jsii_name="alertV2IdInput")
    def alert_v2_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertV2IdInput"))

    @builtins.property
    @jsii.member(jsii_name="appNameInput")
    def app_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizationInput")
    def authorization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizationInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterPolicyIdInput")
    def cluster_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="dashboardIdInput")
    def dashboard_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dashboardIdInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInstanceNameInput")
    def database_instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInstanceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="directoryPathInput")
    def directory_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryPathInput"))

    @builtins.property
    @jsii.member(jsii_name="experimentIdInput")
    def experiment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "experimentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolIdInput")
    def instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="jobIdInput")
    def job_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobIdInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookIdInput")
    def notebook_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notebookIdInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookPathInput")
    def notebook_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notebookPathInput"))

    @builtins.property
    @jsii.member(jsii_name="objectTypeInput")
    def object_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineIdInput")
    def pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineIdInput"))

    @builtins.property
    @jsii.member(jsii_name="registeredModelIdInput")
    def registered_model_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registeredModelIdInput"))

    @builtins.property
    @jsii.member(jsii_name="repoIdInput")
    def repo_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoIdInput"))

    @builtins.property
    @jsii.member(jsii_name="repoPathInput")
    def repo_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoPathInput"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointIdInput")
    def serving_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servingEndpointIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlAlertIdInput")
    def sql_alert_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlAlertIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlDashboardIdInput")
    def sql_dashboard_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlDashboardIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlEndpointIdInput")
    def sql_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlEndpointIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlQueryIdInput")
    def sql_query_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlQueryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="vectorSearchEndpointIdInput")
    def vector_search_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vectorSearchEndpointIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceFileIdInput")
    def workspace_file_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceFileIdInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceFilePathInput")
    def workspace_file_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceFilePathInput"))

    @builtins.property
    @jsii.member(jsii_name="alertV2Id")
    def alert_v2_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertV2Id"))

    @alert_v2_id.setter
    def alert_v2_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__751c791be64b994c21a497d6ffe8488355af9014d4031ead56d05be7b8f50b27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertV2Id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="appName")
    def app_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appName"))

    @app_name.setter
    def app_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef82dcda8028124b62e8bcbf53406de66994e63f3f123f77f65a3339137bd4db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorization")
    def authorization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorization"))

    @authorization.setter
    def authorization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbed1327a42365dd0dfdc203659980be7e9ee8132b248a54179c32233353880b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6667346995b3b226d3bf376117878b6d8b1118eb48d7ad260771416afe3003ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterPolicyId")
    def cluster_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterPolicyId"))

    @cluster_policy_id.setter
    def cluster_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e21d87212e080ac23b8645f74766d7945fd29a7cb183d7d12328e9a18d2cc264)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dashboardId")
    def dashboard_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dashboardId"))

    @dashboard_id.setter
    def dashboard_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e3d4ae5fb536d39314a189193b3554d4d02570f72932f9c3144dc3b2508e08a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dashboardId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databaseInstanceName")
    def database_instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseInstanceName"))

    @database_instance_name.setter
    def database_instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0668430929571c1d0b5f876a137e2d2964fd949b387ac481834381c63dd9bb1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseInstanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74543063339a9b98b5b4303cc37e93d24d512b17a355d28c2c8992d837cc4dda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="directoryPath")
    def directory_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryPath"))

    @directory_path.setter
    def directory_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c79bc6d222228c948882633a00d3f085b2570d2835a4e3339d1ad92fc1b7ff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="experimentId")
    def experiment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "experimentId"))

    @experiment_id.setter
    def experiment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db33f2b8a7d270d42c7a6daa4a8dce3dcf59bf7d1ac68889ac7b113f776db08c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "experimentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__556ad4bfdcc100e6cc2c76dd5ca7e2b59959be4e5bbec50b24f01edd6e96edec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c4f4af3b839cc6e45f52c0b4f878dd584e03c9fff2168d8837646c40181cfd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobId"))

    @job_id.setter
    def job_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d66fcf20cebb2deca8ca49200d21319303e78a2858719ba0a65ca8c1f0893ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notebookId")
    def notebook_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notebookId"))

    @notebook_id.setter
    def notebook_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc06ca2e2c955da4eae1cea8f2bc1d4206fd58195289bff195959458436bccdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebookId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notebookPath")
    def notebook_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notebookPath"))

    @notebook_path.setter
    def notebook_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf62208252b15643f00e96c4dccc0c7650b9a969ae3a78d4827b056ef99c9c2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notebookPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="objectType")
    def object_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectType"))

    @object_type.setter
    def object_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4014b0f043ca0742d38a2235b9b5914ec64d31340016c2db839695f2413548c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @pipeline_id.setter
    def pipeline_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd60cce55d65cae79b0cdb1a1db0bd3f132efd1c2f43dbe9dcf8d5aedc8b768a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="registeredModelId")
    def registered_model_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registeredModelId"))

    @registered_model_id.setter
    def registered_model_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1862fe3e1fcd60bc8c926e9388b90d551193d82b53db95e88bae9cf44a5629d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registeredModelId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repoId")
    def repo_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoId"))

    @repo_id.setter
    def repo_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8960ba97f65904685100737bd9928a804f9231f1f4ef20483934251117a5331)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repoId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repoPath")
    def repo_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoPath"))

    @repo_path.setter
    def repo_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afa33d74e9ea93b0ef0e8162b45c348fdfea031fa365baf57e8fff4470b3d866)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repoPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servingEndpointId")
    def serving_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servingEndpointId"))

    @serving_endpoint_id.setter
    def serving_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7291fe7a47959419523db8c341bcb5a3f055589c76a61798061fcbf360c36f7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servingEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlAlertId")
    def sql_alert_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlAlertId"))

    @sql_alert_id.setter
    def sql_alert_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc4b1c6d8b4b95bbde572896a6e2c689e51d41d842bdfb8d854e52f55581c707)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlAlertId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlDashboardId")
    def sql_dashboard_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlDashboardId"))

    @sql_dashboard_id.setter
    def sql_dashboard_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03789a06c8f475b88b82a78633da74a6623cc7e781391cd1d633f638c6047569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlDashboardId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlEndpointId")
    def sql_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlEndpointId"))

    @sql_endpoint_id.setter
    def sql_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__893dc56e9dbd8e3238817df97485d7c1ba5f69a0b46a598e984a7c3efc88ec57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlQueryId")
    def sql_query_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlQueryId"))

    @sql_query_id.setter
    def sql_query_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e471e6a2c7c4c0bceec2b2288c04d0e8fe32a2b58c0f0e0f5505a488aaaa43e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlQueryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vectorSearchEndpointId")
    def vector_search_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vectorSearchEndpointId"))

    @vector_search_endpoint_id.setter
    def vector_search_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba4268aaa2d5413fcd7b18da63f62007f5f389c02e9abdf5159dc56bd529e469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vectorSearchEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceFileId")
    def workspace_file_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceFileId"))

    @workspace_file_id.setter
    def workspace_file_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2df10fb1243556e139de4b9541b8f813c520e5645e74d4a123091dca0310489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceFileId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceFilePath")
    def workspace_file_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceFilePath"))

    @workspace_file_path.setter
    def workspace_file_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__651dc2f370c50617113f5b0bfabc2a028e9d9b692bf80aef5c22c48c2c32fbf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceFilePath", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.permissions.PermissionsAccessControl",
    jsii_struct_bases=[],
    name_mapping={
        "group_name": "groupName",
        "permission_level": "permissionLevel",
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class PermissionsAccessControl:
    def __init__(
        self,
        *,
        group_name: typing.Optional[builtins.str] = None,
        permission_level: typing.Optional[builtins.str] = None,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#group_name Permissions#group_name}.
        :param permission_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#permission_level Permissions#permission_level}.
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#service_principal_name Permissions#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#user_name Permissions#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5256cb278790e44c15aab2a1a8f32beefb008045b43ec44aa336f0835ee0b026)
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument permission_level", value=permission_level, expected_type=type_hints["permission_level"])
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if group_name is not None:
            self._values["group_name"] = group_name
        if permission_level is not None:
            self._values["permission_level"] = permission_level
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#group_name Permissions#group_name}.'''
        result = self._values.get("group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permission_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#permission_level Permissions#permission_level}.'''
        result = self._values.get("permission_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#service_principal_name Permissions#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#user_name Permissions#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionsAccessControl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PermissionsAccessControlList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.permissions.PermissionsAccessControlList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9059a2e1f2cad85d90e48018d4001a5258ec6c4ea83329e8d79fb2b72728c790)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PermissionsAccessControlOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c08ddda2b63f1f9ba980e94388d8f10518f5538bb42f2620417d18b111359762)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PermissionsAccessControlOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1500af076d28d62bb219eaaec6ba5a577c54d7c27d2ce4f9198cf64b6fe9c4a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__312d4d427559723b39eb8c1fde5765b030641e61b910f5b29c989b483529da73)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b2fc064888835d89a8cd0ef9edff04a2d284853086776c0d0b26cc97cc172e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__269fc5edfb910ede885979700947eaadf0d67385a0eb6dd127bcc45e43fe4ffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PermissionsAccessControlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.permissions.PermissionsAccessControlOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f73a17597045df95b39fd90e745af42029e032b2fb82e81cc0151e6bb47531f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetGroupName")
    def reset_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupName", []))

    @jsii.member(jsii_name="resetPermissionLevel")
    def reset_permission_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissionLevel", []))

    @jsii.member(jsii_name="resetServicePrincipalName")
    def reset_service_principal_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServicePrincipalName", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

    @builtins.property
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionLevelInput")
    def permission_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalNameInput")
    def service_principal_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servicePrincipalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb7b4ec964d7d78993f3ba48c14d54f4046167c799aa7e124bffff1334ebba1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permissionLevel")
    def permission_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionLevel"))

    @permission_level.setter
    def permission_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ba1542009504cdf694b10fd8bbeb62d1b001e6eb8eab30efd36f3ada01fe0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permissionLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalName")
    def service_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalName"))

    @service_principal_name.setter
    def service_principal_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca297297c5af241643a2dccadd1c05a8c53ef64b25aa05b506522a21db69ae9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a8d6ff79e89245fd9bf04a6c1b9b6a7e9fdd7cb8dea6333188c8c1de2b11406)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PermissionsAccessControl]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PermissionsAccessControl]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PermissionsAccessControl]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a5d1987c4d1e65c004cf4e3a07b1389ce92097283f9e661db9f3d09beed6fb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.permissions.PermissionsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "access_control": "accessControl",
        "alert_v2_id": "alertV2Id",
        "app_name": "appName",
        "authorization": "authorization",
        "cluster_id": "clusterId",
        "cluster_policy_id": "clusterPolicyId",
        "dashboard_id": "dashboardId",
        "database_instance_name": "databaseInstanceName",
        "directory_id": "directoryId",
        "directory_path": "directoryPath",
        "experiment_id": "experimentId",
        "id": "id",
        "instance_pool_id": "instancePoolId",
        "job_id": "jobId",
        "notebook_id": "notebookId",
        "notebook_path": "notebookPath",
        "object_type": "objectType",
        "pipeline_id": "pipelineId",
        "registered_model_id": "registeredModelId",
        "repo_id": "repoId",
        "repo_path": "repoPath",
        "serving_endpoint_id": "servingEndpointId",
        "sql_alert_id": "sqlAlertId",
        "sql_dashboard_id": "sqlDashboardId",
        "sql_endpoint_id": "sqlEndpointId",
        "sql_query_id": "sqlQueryId",
        "vector_search_endpoint_id": "vectorSearchEndpointId",
        "workspace_file_id": "workspaceFileId",
        "workspace_file_path": "workspaceFilePath",
    },
)
class PermissionsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_control: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PermissionsAccessControl, typing.Dict[builtins.str, typing.Any]]]],
        alert_v2_id: typing.Optional[builtins.str] = None,
        app_name: typing.Optional[builtins.str] = None,
        authorization: typing.Optional[builtins.str] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        cluster_policy_id: typing.Optional[builtins.str] = None,
        dashboard_id: typing.Optional[builtins.str] = None,
        database_instance_name: typing.Optional[builtins.str] = None,
        directory_id: typing.Optional[builtins.str] = None,
        directory_path: typing.Optional[builtins.str] = None,
        experiment_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        job_id: typing.Optional[builtins.str] = None,
        notebook_id: typing.Optional[builtins.str] = None,
        notebook_path: typing.Optional[builtins.str] = None,
        object_type: typing.Optional[builtins.str] = None,
        pipeline_id: typing.Optional[builtins.str] = None,
        registered_model_id: typing.Optional[builtins.str] = None,
        repo_id: typing.Optional[builtins.str] = None,
        repo_path: typing.Optional[builtins.str] = None,
        serving_endpoint_id: typing.Optional[builtins.str] = None,
        sql_alert_id: typing.Optional[builtins.str] = None,
        sql_dashboard_id: typing.Optional[builtins.str] = None,
        sql_endpoint_id: typing.Optional[builtins.str] = None,
        sql_query_id: typing.Optional[builtins.str] = None,
        vector_search_endpoint_id: typing.Optional[builtins.str] = None,
        workspace_file_id: typing.Optional[builtins.str] = None,
        workspace_file_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param access_control: access_control block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#access_control Permissions#access_control}
        :param alert_v2_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#alert_v2_id Permissions#alert_v2_id}.
        :param app_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#app_name Permissions#app_name}.
        :param authorization: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#authorization Permissions#authorization}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_id Permissions#cluster_id}.
        :param cluster_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_policy_id Permissions#cluster_policy_id}.
        :param dashboard_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#dashboard_id Permissions#dashboard_id}.
        :param database_instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#database_instance_name Permissions#database_instance_name}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_id Permissions#directory_id}.
        :param directory_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_path Permissions#directory_path}.
        :param experiment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#experiment_id Permissions#experiment_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#id Permissions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#instance_pool_id Permissions#instance_pool_id}.
        :param job_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#job_id Permissions#job_id}.
        :param notebook_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_id Permissions#notebook_id}.
        :param notebook_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_path Permissions#notebook_path}.
        :param object_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#object_type Permissions#object_type}.
        :param pipeline_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#pipeline_id Permissions#pipeline_id}.
        :param registered_model_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#registered_model_id Permissions#registered_model_id}.
        :param repo_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_id Permissions#repo_id}.
        :param repo_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_path Permissions#repo_path}.
        :param serving_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#serving_endpoint_id Permissions#serving_endpoint_id}.
        :param sql_alert_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_alert_id Permissions#sql_alert_id}.
        :param sql_dashboard_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_dashboard_id Permissions#sql_dashboard_id}.
        :param sql_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_endpoint_id Permissions#sql_endpoint_id}.
        :param sql_query_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_query_id Permissions#sql_query_id}.
        :param vector_search_endpoint_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#vector_search_endpoint_id Permissions#vector_search_endpoint_id}.
        :param workspace_file_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_id Permissions#workspace_file_id}.
        :param workspace_file_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_path Permissions#workspace_file_path}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1347c4a058745dd645e5c6d460aad02194c2952936ce99aad6d438e7ab8e7951)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument alert_v2_id", value=alert_v2_id, expected_type=type_hints["alert_v2_id"])
            check_type(argname="argument app_name", value=app_name, expected_type=type_hints["app_name"])
            check_type(argname="argument authorization", value=authorization, expected_type=type_hints["authorization"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument cluster_policy_id", value=cluster_policy_id, expected_type=type_hints["cluster_policy_id"])
            check_type(argname="argument dashboard_id", value=dashboard_id, expected_type=type_hints["dashboard_id"])
            check_type(argname="argument database_instance_name", value=database_instance_name, expected_type=type_hints["database_instance_name"])
            check_type(argname="argument directory_id", value=directory_id, expected_type=type_hints["directory_id"])
            check_type(argname="argument directory_path", value=directory_path, expected_type=type_hints["directory_path"])
            check_type(argname="argument experiment_id", value=experiment_id, expected_type=type_hints["experiment_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument job_id", value=job_id, expected_type=type_hints["job_id"])
            check_type(argname="argument notebook_id", value=notebook_id, expected_type=type_hints["notebook_id"])
            check_type(argname="argument notebook_path", value=notebook_path, expected_type=type_hints["notebook_path"])
            check_type(argname="argument object_type", value=object_type, expected_type=type_hints["object_type"])
            check_type(argname="argument pipeline_id", value=pipeline_id, expected_type=type_hints["pipeline_id"])
            check_type(argname="argument registered_model_id", value=registered_model_id, expected_type=type_hints["registered_model_id"])
            check_type(argname="argument repo_id", value=repo_id, expected_type=type_hints["repo_id"])
            check_type(argname="argument repo_path", value=repo_path, expected_type=type_hints["repo_path"])
            check_type(argname="argument serving_endpoint_id", value=serving_endpoint_id, expected_type=type_hints["serving_endpoint_id"])
            check_type(argname="argument sql_alert_id", value=sql_alert_id, expected_type=type_hints["sql_alert_id"])
            check_type(argname="argument sql_dashboard_id", value=sql_dashboard_id, expected_type=type_hints["sql_dashboard_id"])
            check_type(argname="argument sql_endpoint_id", value=sql_endpoint_id, expected_type=type_hints["sql_endpoint_id"])
            check_type(argname="argument sql_query_id", value=sql_query_id, expected_type=type_hints["sql_query_id"])
            check_type(argname="argument vector_search_endpoint_id", value=vector_search_endpoint_id, expected_type=type_hints["vector_search_endpoint_id"])
            check_type(argname="argument workspace_file_id", value=workspace_file_id, expected_type=type_hints["workspace_file_id"])
            check_type(argname="argument workspace_file_path", value=workspace_file_path, expected_type=type_hints["workspace_file_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_control": access_control,
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
        if alert_v2_id is not None:
            self._values["alert_v2_id"] = alert_v2_id
        if app_name is not None:
            self._values["app_name"] = app_name
        if authorization is not None:
            self._values["authorization"] = authorization
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if cluster_policy_id is not None:
            self._values["cluster_policy_id"] = cluster_policy_id
        if dashboard_id is not None:
            self._values["dashboard_id"] = dashboard_id
        if database_instance_name is not None:
            self._values["database_instance_name"] = database_instance_name
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if directory_path is not None:
            self._values["directory_path"] = directory_path
        if experiment_id is not None:
            self._values["experiment_id"] = experiment_id
        if id is not None:
            self._values["id"] = id
        if instance_pool_id is not None:
            self._values["instance_pool_id"] = instance_pool_id
        if job_id is not None:
            self._values["job_id"] = job_id
        if notebook_id is not None:
            self._values["notebook_id"] = notebook_id
        if notebook_path is not None:
            self._values["notebook_path"] = notebook_path
        if object_type is not None:
            self._values["object_type"] = object_type
        if pipeline_id is not None:
            self._values["pipeline_id"] = pipeline_id
        if registered_model_id is not None:
            self._values["registered_model_id"] = registered_model_id
        if repo_id is not None:
            self._values["repo_id"] = repo_id
        if repo_path is not None:
            self._values["repo_path"] = repo_path
        if serving_endpoint_id is not None:
            self._values["serving_endpoint_id"] = serving_endpoint_id
        if sql_alert_id is not None:
            self._values["sql_alert_id"] = sql_alert_id
        if sql_dashboard_id is not None:
            self._values["sql_dashboard_id"] = sql_dashboard_id
        if sql_endpoint_id is not None:
            self._values["sql_endpoint_id"] = sql_endpoint_id
        if sql_query_id is not None:
            self._values["sql_query_id"] = sql_query_id
        if vector_search_endpoint_id is not None:
            self._values["vector_search_endpoint_id"] = vector_search_endpoint_id
        if workspace_file_id is not None:
            self._values["workspace_file_id"] = workspace_file_id
        if workspace_file_path is not None:
            self._values["workspace_file_path"] = workspace_file_path

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
    def access_control(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]]:
        '''access_control block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#access_control Permissions#access_control}
        '''
        result = self._values.get("access_control")
        assert result is not None, "Required property 'access_control' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]], result)

    @builtins.property
    def alert_v2_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#alert_v2_id Permissions#alert_v2_id}.'''
        result = self._values.get("alert_v2_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#app_name Permissions#app_name}.'''
        result = self._values.get("app_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#authorization Permissions#authorization}.'''
        result = self._values.get("authorization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_id Permissions#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#cluster_policy_id Permissions#cluster_policy_id}.'''
        result = self._values.get("cluster_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dashboard_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#dashboard_id Permissions#dashboard_id}.'''
        result = self._values.get("dashboard_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_instance_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#database_instance_name Permissions#database_instance_name}.'''
        result = self._values.get("database_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_id Permissions#directory_id}.'''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directory_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#directory_path Permissions#directory_path}.'''
        result = self._values.get("directory_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def experiment_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#experiment_id Permissions#experiment_id}.'''
        result = self._values.get("experiment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#id Permissions#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#instance_pool_id Permissions#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#job_id Permissions#job_id}.'''
        result = self._values.get("job_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notebook_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_id Permissions#notebook_id}.'''
        result = self._values.get("notebook_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notebook_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#notebook_path Permissions#notebook_path}.'''
        result = self._values.get("notebook_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#object_type Permissions#object_type}.'''
        result = self._values.get("object_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#pipeline_id Permissions#pipeline_id}.'''
        result = self._values.get("pipeline_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registered_model_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#registered_model_id Permissions#registered_model_id}.'''
        result = self._values.get("registered_model_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_id Permissions#repo_id}.'''
        result = self._values.get("repo_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#repo_path Permissions#repo_path}.'''
        result = self._values.get("repo_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serving_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#serving_endpoint_id Permissions#serving_endpoint_id}.'''
        result = self._values.get("serving_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_alert_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_alert_id Permissions#sql_alert_id}.'''
        result = self._values.get("sql_alert_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_dashboard_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_dashboard_id Permissions#sql_dashboard_id}.'''
        result = self._values.get("sql_dashboard_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_endpoint_id Permissions#sql_endpoint_id}.'''
        result = self._values.get("sql_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_query_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#sql_query_id Permissions#sql_query_id}.'''
        result = self._values.get("sql_query_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vector_search_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#vector_search_endpoint_id Permissions#vector_search_endpoint_id}.'''
        result = self._values.get("vector_search_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_file_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_id Permissions#workspace_file_id}.'''
        result = self._values.get("workspace_file_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_file_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/permissions#workspace_file_path Permissions#workspace_file_path}.'''
        result = self._values.get("workspace_file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Permissions",
    "PermissionsAccessControl",
    "PermissionsAccessControlList",
    "PermissionsAccessControlOutputReference",
    "PermissionsConfig",
]

publication.publish()

def _typecheckingstub__1a98068f475c3ee349d67d2fb8108b3fcb806e359f2766e26580cd4d2c5e72a7(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    access_control: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PermissionsAccessControl, typing.Dict[builtins.str, typing.Any]]]],
    alert_v2_id: typing.Optional[builtins.str] = None,
    app_name: typing.Optional[builtins.str] = None,
    authorization: typing.Optional[builtins.str] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    cluster_policy_id: typing.Optional[builtins.str] = None,
    dashboard_id: typing.Optional[builtins.str] = None,
    database_instance_name: typing.Optional[builtins.str] = None,
    directory_id: typing.Optional[builtins.str] = None,
    directory_path: typing.Optional[builtins.str] = None,
    experiment_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    job_id: typing.Optional[builtins.str] = None,
    notebook_id: typing.Optional[builtins.str] = None,
    notebook_path: typing.Optional[builtins.str] = None,
    object_type: typing.Optional[builtins.str] = None,
    pipeline_id: typing.Optional[builtins.str] = None,
    registered_model_id: typing.Optional[builtins.str] = None,
    repo_id: typing.Optional[builtins.str] = None,
    repo_path: typing.Optional[builtins.str] = None,
    serving_endpoint_id: typing.Optional[builtins.str] = None,
    sql_alert_id: typing.Optional[builtins.str] = None,
    sql_dashboard_id: typing.Optional[builtins.str] = None,
    sql_endpoint_id: typing.Optional[builtins.str] = None,
    sql_query_id: typing.Optional[builtins.str] = None,
    vector_search_endpoint_id: typing.Optional[builtins.str] = None,
    workspace_file_id: typing.Optional[builtins.str] = None,
    workspace_file_path: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__afad0ec134fdc626669ab9a7402c28cde2875df634e69b5b0e9837a4a2dd2352(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d52cb408a8c6c421d42275c3fa76c41242be248c46b596dc95b424a836775c93(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PermissionsAccessControl, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751c791be64b994c21a497d6ffe8488355af9014d4031ead56d05be7b8f50b27(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef82dcda8028124b62e8bcbf53406de66994e63f3f123f77f65a3339137bd4db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbed1327a42365dd0dfdc203659980be7e9ee8132b248a54179c32233353880b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6667346995b3b226d3bf376117878b6d8b1118eb48d7ad260771416afe3003ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21d87212e080ac23b8645f74766d7945fd29a7cb183d7d12328e9a18d2cc264(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e3d4ae5fb536d39314a189193b3554d4d02570f72932f9c3144dc3b2508e08a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0668430929571c1d0b5f876a137e2d2964fd949b387ac481834381c63dd9bb1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74543063339a9b98b5b4303cc37e93d24d512b17a355d28c2c8992d837cc4dda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c79bc6d222228c948882633a00d3f085b2570d2835a4e3339d1ad92fc1b7ff4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db33f2b8a7d270d42c7a6daa4a8dce3dcf59bf7d1ac68889ac7b113f776db08c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__556ad4bfdcc100e6cc2c76dd5ca7e2b59959be4e5bbec50b24f01edd6e96edec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c4f4af3b839cc6e45f52c0b4f878dd584e03c9fff2168d8837646c40181cfd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d66fcf20cebb2deca8ca49200d21319303e78a2858719ba0a65ca8c1f0893ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc06ca2e2c955da4eae1cea8f2bc1d4206fd58195289bff195959458436bccdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf62208252b15643f00e96c4dccc0c7650b9a969ae3a78d4827b056ef99c9c2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4014b0f043ca0742d38a2235b9b5914ec64d31340016c2db839695f2413548c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd60cce55d65cae79b0cdb1a1db0bd3f132efd1c2f43dbe9dcf8d5aedc8b768a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1862fe3e1fcd60bc8c926e9388b90d551193d82b53db95e88bae9cf44a5629d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8960ba97f65904685100737bd9928a804f9231f1f4ef20483934251117a5331(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afa33d74e9ea93b0ef0e8162b45c348fdfea031fa365baf57e8fff4470b3d866(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7291fe7a47959419523db8c341bcb5a3f055589c76a61798061fcbf360c36f7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc4b1c6d8b4b95bbde572896a6e2c689e51d41d842bdfb8d854e52f55581c707(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03789a06c8f475b88b82a78633da74a6623cc7e781391cd1d633f638c6047569(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893dc56e9dbd8e3238817df97485d7c1ba5f69a0b46a598e984a7c3efc88ec57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e471e6a2c7c4c0bceec2b2288c04d0e8fe32a2b58c0f0e0f5505a488aaaa43e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba4268aaa2d5413fcd7b18da63f62007f5f389c02e9abdf5159dc56bd529e469(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2df10fb1243556e139de4b9541b8f813c520e5645e74d4a123091dca0310489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__651dc2f370c50617113f5b0bfabc2a028e9d9b692bf80aef5c22c48c2c32fbf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5256cb278790e44c15aab2a1a8f32beefb008045b43ec44aa336f0835ee0b026(
    *,
    group_name: typing.Optional[builtins.str] = None,
    permission_level: typing.Optional[builtins.str] = None,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9059a2e1f2cad85d90e48018d4001a5258ec6c4ea83329e8d79fb2b72728c790(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c08ddda2b63f1f9ba980e94388d8f10518f5538bb42f2620417d18b111359762(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1500af076d28d62bb219eaaec6ba5a577c54d7c27d2ce4f9198cf64b6fe9c4a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312d4d427559723b39eb8c1fde5765b030641e61b910f5b29c989b483529da73(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b2fc064888835d89a8cd0ef9edff04a2d284853086776c0d0b26cc97cc172e1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__269fc5edfb910ede885979700947eaadf0d67385a0eb6dd127bcc45e43fe4ffd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PermissionsAccessControl]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f73a17597045df95b39fd90e745af42029e032b2fb82e81cc0151e6bb47531f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb7b4ec964d7d78993f3ba48c14d54f4046167c799aa7e124bffff1334ebba1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ba1542009504cdf694b10fd8bbeb62d1b001e6eb8eab30efd36f3ada01fe0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca297297c5af241643a2dccadd1c05a8c53ef64b25aa05b506522a21db69ae9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a8d6ff79e89245fd9bf04a6c1b9b6a7e9fdd7cb8dea6333188c8c1de2b11406(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a5d1987c4d1e65c004cf4e3a07b1389ce92097283f9e661db9f3d09beed6fb1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PermissionsAccessControl]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1347c4a058745dd645e5c6d460aad02194c2952936ce99aad6d438e7ab8e7951(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    access_control: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PermissionsAccessControl, typing.Dict[builtins.str, typing.Any]]]],
    alert_v2_id: typing.Optional[builtins.str] = None,
    app_name: typing.Optional[builtins.str] = None,
    authorization: typing.Optional[builtins.str] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    cluster_policy_id: typing.Optional[builtins.str] = None,
    dashboard_id: typing.Optional[builtins.str] = None,
    database_instance_name: typing.Optional[builtins.str] = None,
    directory_id: typing.Optional[builtins.str] = None,
    directory_path: typing.Optional[builtins.str] = None,
    experiment_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    job_id: typing.Optional[builtins.str] = None,
    notebook_id: typing.Optional[builtins.str] = None,
    notebook_path: typing.Optional[builtins.str] = None,
    object_type: typing.Optional[builtins.str] = None,
    pipeline_id: typing.Optional[builtins.str] = None,
    registered_model_id: typing.Optional[builtins.str] = None,
    repo_id: typing.Optional[builtins.str] = None,
    repo_path: typing.Optional[builtins.str] = None,
    serving_endpoint_id: typing.Optional[builtins.str] = None,
    sql_alert_id: typing.Optional[builtins.str] = None,
    sql_dashboard_id: typing.Optional[builtins.str] = None,
    sql_endpoint_id: typing.Optional[builtins.str] = None,
    sql_query_id: typing.Optional[builtins.str] = None,
    vector_search_endpoint_id: typing.Optional[builtins.str] = None,
    workspace_file_id: typing.Optional[builtins.str] = None,
    workspace_file_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
