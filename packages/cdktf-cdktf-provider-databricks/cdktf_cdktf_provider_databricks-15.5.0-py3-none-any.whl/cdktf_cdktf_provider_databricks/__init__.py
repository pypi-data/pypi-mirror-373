r'''
# CDKTF prebuilt bindings for databricks/databricks provider version 1.88.0

This repo builds and publishes the [Terraform databricks provider](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-databricks](https://www.npmjs.com/package/@cdktf/provider-databricks).

`npm install @cdktf/provider-databricks`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-databricks](https://pypi.org/project/cdktf-cdktf-provider-databricks).

`pipenv install cdktf-cdktf-provider-databricks`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Databricks](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Databricks).

`dotnet add package HashiCorp.Cdktf.Providers.Databricks`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-databricks](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-databricks).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-databricks</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-databricks-go`](https://github.com/cdktf/cdktf-provider-databricks-go) package.

`go get github.com/cdktf/cdktf-provider-databricks-go/databricks/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-databricks-go/blob/main/databricks/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-databricks).

## Versioning

This project is explicitly not tracking the Terraform databricks provider version 1:1. In fact, it always tracks `latest` of `~> 1.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform databricks provider](https://registry.terraform.io/providers/databricks/databricks/1.88.0)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "access_control_rule_set",
    "account_federation_policy",
    "account_network_policy",
    "account_setting_v2",
    "aibi_dashboard_embedding_access_policy_setting",
    "aibi_dashboard_embedding_approved_domains_setting",
    "alert",
    "alert_v2",
    "app",
    "apps_settings_custom_template",
    "artifact_allowlist",
    "automatic_cluster_update_workspace_setting",
    "aws_s3_mount",
    "azure_adls_gen1_mount",
    "azure_adls_gen2_mount",
    "azure_blob_mount",
    "budget",
    "budget_policy",
    "catalog",
    "catalog_workspace_binding",
    "clean_room_asset",
    "clean_room_auto_approval_rule",
    "clean_rooms_clean_room",
    "cluster",
    "cluster_policy",
    "compliance_security_profile_workspace_setting",
    "connection",
    "credential",
    "custom_app_integration",
    "dashboard",
    "data_databricks_account_federation_policies",
    "data_databricks_account_federation_policy",
    "data_databricks_account_network_policies",
    "data_databricks_account_network_policy",
    "data_databricks_account_setting_v2",
    "data_databricks_alert_v2",
    "data_databricks_alerts_v2",
    "data_databricks_app",
    "data_databricks_apps",
    "data_databricks_apps_settings_custom_template",
    "data_databricks_apps_settings_custom_templates",
    "data_databricks_aws_assume_role_policy",
    "data_databricks_aws_bucket_policy",
    "data_databricks_aws_crossaccount_policy",
    "data_databricks_aws_unity_catalog_assume_role_policy",
    "data_databricks_aws_unity_catalog_policy",
    "data_databricks_budget_policies",
    "data_databricks_budget_policy",
    "data_databricks_catalog",
    "data_databricks_catalogs",
    "data_databricks_clean_room_asset",
    "data_databricks_clean_room_asset_revisions_clean_room_asset",
    "data_databricks_clean_room_asset_revisions_clean_room_assets",
    "data_databricks_clean_room_assets",
    "data_databricks_clean_room_auto_approval_rule",
    "data_databricks_clean_room_auto_approval_rules",
    "data_databricks_clean_rooms_clean_room",
    "data_databricks_clean_rooms_clean_rooms",
    "data_databricks_cluster",
    "data_databricks_cluster_pluginframework",
    "data_databricks_cluster_policy",
    "data_databricks_clusters",
    "data_databricks_current_config",
    "data_databricks_current_metastore",
    "data_databricks_current_user",
    "data_databricks_dashboards",
    "data_databricks_database_database_catalog",
    "data_databricks_database_database_catalogs",
    "data_databricks_database_instance",
    "data_databricks_database_instances",
    "data_databricks_database_synced_database_table",
    "data_databricks_database_synced_database_tables",
    "data_databricks_dbfs_file",
    "data_databricks_dbfs_file_paths",
    "data_databricks_directory",
    "data_databricks_entity_tag_assignment",
    "data_databricks_entity_tag_assignments",
    "data_databricks_external_location",
    "data_databricks_external_locations",
    "data_databricks_external_metadata",
    "data_databricks_external_metadatas",
    "data_databricks_functions",
    "data_databricks_group",
    "data_databricks_instance_pool",
    "data_databricks_instance_profiles",
    "data_databricks_job",
    "data_databricks_jobs",
    "data_databricks_materialized_features_feature_tag",
    "data_databricks_materialized_features_feature_tags",
    "data_databricks_metastore",
    "data_databricks_metastores",
    "data_databricks_mlflow_experiment",
    "data_databricks_mlflow_model",
    "data_databricks_mlflow_models",
    "data_databricks_mws_credentials",
    "data_databricks_mws_network_connectivity_config",
    "data_databricks_mws_network_connectivity_configs",
    "data_databricks_mws_workspaces",
    "data_databricks_node_type",
    "data_databricks_notebook",
    "data_databricks_notebook_paths",
    "data_databricks_notification_destinations",
    "data_databricks_online_store",
    "data_databricks_online_stores",
    "data_databricks_pipelines",
    "data_databricks_policy_info",
    "data_databricks_policy_infos",
    "data_databricks_quality_monitor_v2",
    "data_databricks_quality_monitors_v2",
    "data_databricks_recipient_federation_policies",
    "data_databricks_recipient_federation_policy",
    "data_databricks_registered_model",
    "data_databricks_registered_model_versions",
    "data_databricks_schema",
    "data_databricks_schemas",
    "data_databricks_service_principal",
    "data_databricks_service_principal_federation_policies",
    "data_databricks_service_principal_federation_policy",
    "data_databricks_service_principals",
    "data_databricks_serving_endpoints",
    "data_databricks_share",
    "data_databricks_share_pluginframework",
    "data_databricks_shares",
    "data_databricks_shares_pluginframework",
    "data_databricks_spark_version",
    "data_databricks_sql_warehouse",
    "data_databricks_sql_warehouses",
    "data_databricks_storage_credential",
    "data_databricks_storage_credentials",
    "data_databricks_table",
    "data_databricks_tables",
    "data_databricks_tag_policies",
    "data_databricks_tag_policy",
    "data_databricks_user",
    "data_databricks_views",
    "data_databricks_volume",
    "data_databricks_volumes",
    "data_databricks_workspace_network_option",
    "data_databricks_workspace_setting_v2",
    "data_databricks_zones",
    "database_database_catalog",
    "database_instance",
    "database_synced_database_table",
    "dbfs_file",
    "default_namespace_setting",
    "directory",
    "disable_legacy_access_setting",
    "disable_legacy_dbfs_setting",
    "disable_legacy_features_setting",
    "enhanced_security_monitoring_workspace_setting",
    "entitlements",
    "entity_tag_assignment",
    "external_location",
    "external_metadata",
    "file",
    "git_credential",
    "global_init_script",
    "grant",
    "grants",
    "group",
    "group_instance_profile",
    "group_member",
    "group_role",
    "instance_pool",
    "instance_profile",
    "ip_access_list",
    "job",
    "lakehouse_monitor",
    "library",
    "materialized_features_feature_tag",
    "metastore",
    "metastore_assignment",
    "metastore_data_access",
    "mlflow_experiment",
    "mlflow_model",
    "mlflow_webhook",
    "model_serving",
    "model_serving_provisioned_throughput",
    "mount",
    "mws_credentials",
    "mws_customer_managed_keys",
    "mws_log_delivery",
    "mws_ncc_binding",
    "mws_ncc_private_endpoint_rule",
    "mws_network_connectivity_config",
    "mws_networks",
    "mws_permission_assignment",
    "mws_private_access_settings",
    "mws_storage_configurations",
    "mws_vpc_endpoint",
    "mws_workspaces",
    "notebook",
    "notification_destination",
    "obo_token",
    "online_store",
    "online_table",
    "permission_assignment",
    "permissions",
    "pipeline",
    "policy_info",
    "provider",
    "provider_resource",
    "quality_monitor",
    "quality_monitor_v2",
    "query",
    "recipient",
    "recipient_federation_policy",
    "registered_model",
    "repo",
    "restrict_workspace_admins_setting",
    "schema",
    "secret",
    "secret_acl",
    "secret_scope",
    "service_principal",
    "service_principal_federation_policy",
    "service_principal_role",
    "service_principal_secret",
    "share",
    "share_pluginframework",
    "sql_alert",
    "sql_dashboard",
    "sql_endpoint",
    "sql_global_config",
    "sql_permissions",
    "sql_query",
    "sql_table",
    "sql_visualization",
    "sql_widget",
    "storage_credential",
    "system_schema",
    "table",
    "tag_policy",
    "token",
    "user",
    "user_instance_profile",
    "user_role",
    "vector_search_endpoint",
    "vector_search_index",
    "volume",
    "workspace_binding",
    "workspace_conf",
    "workspace_file",
    "workspace_network_option",
    "workspace_setting_v2",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import access_control_rule_set
from . import account_federation_policy
from . import account_network_policy
from . import account_setting_v2
from . import aibi_dashboard_embedding_access_policy_setting
from . import aibi_dashboard_embedding_approved_domains_setting
from . import alert
from . import alert_v2
from . import app
from . import apps_settings_custom_template
from . import artifact_allowlist
from . import automatic_cluster_update_workspace_setting
from . import aws_s3_mount
from . import azure_adls_gen1_mount
from . import azure_adls_gen2_mount
from . import azure_blob_mount
from . import budget
from . import budget_policy
from . import catalog
from . import catalog_workspace_binding
from . import clean_room_asset
from . import clean_room_auto_approval_rule
from . import clean_rooms_clean_room
from . import cluster
from . import cluster_policy
from . import compliance_security_profile_workspace_setting
from . import connection
from . import credential
from . import custom_app_integration
from . import dashboard
from . import data_databricks_account_federation_policies
from . import data_databricks_account_federation_policy
from . import data_databricks_account_network_policies
from . import data_databricks_account_network_policy
from . import data_databricks_account_setting_v2
from . import data_databricks_alert_v2
from . import data_databricks_alerts_v2
from . import data_databricks_app
from . import data_databricks_apps
from . import data_databricks_apps_settings_custom_template
from . import data_databricks_apps_settings_custom_templates
from . import data_databricks_aws_assume_role_policy
from . import data_databricks_aws_bucket_policy
from . import data_databricks_aws_crossaccount_policy
from . import data_databricks_aws_unity_catalog_assume_role_policy
from . import data_databricks_aws_unity_catalog_policy
from . import data_databricks_budget_policies
from . import data_databricks_budget_policy
from . import data_databricks_catalog
from . import data_databricks_catalogs
from . import data_databricks_clean_room_asset
from . import data_databricks_clean_room_asset_revisions_clean_room_asset
from . import data_databricks_clean_room_asset_revisions_clean_room_assets
from . import data_databricks_clean_room_assets
from . import data_databricks_clean_room_auto_approval_rule
from . import data_databricks_clean_room_auto_approval_rules
from . import data_databricks_clean_rooms_clean_room
from . import data_databricks_clean_rooms_clean_rooms
from . import data_databricks_cluster
from . import data_databricks_cluster_pluginframework
from . import data_databricks_cluster_policy
from . import data_databricks_clusters
from . import data_databricks_current_config
from . import data_databricks_current_metastore
from . import data_databricks_current_user
from . import data_databricks_dashboards
from . import data_databricks_database_database_catalog
from . import data_databricks_database_database_catalogs
from . import data_databricks_database_instance
from . import data_databricks_database_instances
from . import data_databricks_database_synced_database_table
from . import data_databricks_database_synced_database_tables
from . import data_databricks_dbfs_file
from . import data_databricks_dbfs_file_paths
from . import data_databricks_directory
from . import data_databricks_entity_tag_assignment
from . import data_databricks_entity_tag_assignments
from . import data_databricks_external_location
from . import data_databricks_external_locations
from . import data_databricks_external_metadata
from . import data_databricks_external_metadatas
from . import data_databricks_functions
from . import data_databricks_group
from . import data_databricks_instance_pool
from . import data_databricks_instance_profiles
from . import data_databricks_job
from . import data_databricks_jobs
from . import data_databricks_materialized_features_feature_tag
from . import data_databricks_materialized_features_feature_tags
from . import data_databricks_metastore
from . import data_databricks_metastores
from . import data_databricks_mlflow_experiment
from . import data_databricks_mlflow_model
from . import data_databricks_mlflow_models
from . import data_databricks_mws_credentials
from . import data_databricks_mws_network_connectivity_config
from . import data_databricks_mws_network_connectivity_configs
from . import data_databricks_mws_workspaces
from . import data_databricks_node_type
from . import data_databricks_notebook
from . import data_databricks_notebook_paths
from . import data_databricks_notification_destinations
from . import data_databricks_online_store
from . import data_databricks_online_stores
from . import data_databricks_pipelines
from . import data_databricks_policy_info
from . import data_databricks_policy_infos
from . import data_databricks_quality_monitor_v2
from . import data_databricks_quality_monitors_v2
from . import data_databricks_recipient_federation_policies
from . import data_databricks_recipient_federation_policy
from . import data_databricks_registered_model
from . import data_databricks_registered_model_versions
from . import data_databricks_schema
from . import data_databricks_schemas
from . import data_databricks_service_principal
from . import data_databricks_service_principal_federation_policies
from . import data_databricks_service_principal_federation_policy
from . import data_databricks_service_principals
from . import data_databricks_serving_endpoints
from . import data_databricks_share
from . import data_databricks_share_pluginframework
from . import data_databricks_shares
from . import data_databricks_shares_pluginframework
from . import data_databricks_spark_version
from . import data_databricks_sql_warehouse
from . import data_databricks_sql_warehouses
from . import data_databricks_storage_credential
from . import data_databricks_storage_credentials
from . import data_databricks_table
from . import data_databricks_tables
from . import data_databricks_tag_policies
from . import data_databricks_tag_policy
from . import data_databricks_user
from . import data_databricks_views
from . import data_databricks_volume
from . import data_databricks_volumes
from . import data_databricks_workspace_network_option
from . import data_databricks_workspace_setting_v2
from . import data_databricks_zones
from . import database_database_catalog
from . import database_instance
from . import database_synced_database_table
from . import dbfs_file
from . import default_namespace_setting
from . import directory
from . import disable_legacy_access_setting
from . import disable_legacy_dbfs_setting
from . import disable_legacy_features_setting
from . import enhanced_security_monitoring_workspace_setting
from . import entitlements
from . import entity_tag_assignment
from . import external_location
from . import external_metadata
from . import file
from . import git_credential
from . import global_init_script
from . import grant
from . import grants
from . import group
from . import group_instance_profile
from . import group_member
from . import group_role
from . import instance_pool
from . import instance_profile
from . import ip_access_list
from . import job
from . import lakehouse_monitor
from . import library
from . import materialized_features_feature_tag
from . import metastore
from . import metastore_assignment
from . import metastore_data_access
from . import mlflow_experiment
from . import mlflow_model
from . import mlflow_webhook
from . import model_serving
from . import model_serving_provisioned_throughput
from . import mount
from . import mws_credentials
from . import mws_customer_managed_keys
from . import mws_log_delivery
from . import mws_ncc_binding
from . import mws_ncc_private_endpoint_rule
from . import mws_network_connectivity_config
from . import mws_networks
from . import mws_permission_assignment
from . import mws_private_access_settings
from . import mws_storage_configurations
from . import mws_vpc_endpoint
from . import mws_workspaces
from . import notebook
from . import notification_destination
from . import obo_token
from . import online_store
from . import online_table
from . import permission_assignment
from . import permissions
from . import pipeline
from . import policy_info
from . import provider
from . import provider_resource
from . import quality_monitor
from . import quality_monitor_v2
from . import query
from . import recipient
from . import recipient_federation_policy
from . import registered_model
from . import repo
from . import restrict_workspace_admins_setting
from . import schema
from . import secret
from . import secret_acl
from . import secret_scope
from . import service_principal
from . import service_principal_federation_policy
from . import service_principal_role
from . import service_principal_secret
from . import share
from . import share_pluginframework
from . import sql_alert
from . import sql_dashboard
from . import sql_endpoint
from . import sql_global_config
from . import sql_permissions
from . import sql_query
from . import sql_table
from . import sql_visualization
from . import sql_widget
from . import storage_credential
from . import system_schema
from . import table
from . import tag_policy
from . import token
from . import user
from . import user_instance_profile
from . import user_role
from . import vector_search_endpoint
from . import vector_search_index
from . import volume
from . import workspace_binding
from . import workspace_conf
from . import workspace_file
from . import workspace_network_option
from . import workspace_setting_v2
