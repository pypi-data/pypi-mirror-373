r'''
# `provider`

Refer to the Terraform Registry for docs: [`databricks`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs).
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


class DatabricksProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.provider.DatabricksProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs databricks}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        actions_id_token_request_token: typing.Optional[builtins.str] = None,
        actions_id_token_request_url: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        audience: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        azure_client_id: typing.Optional[builtins.str] = None,
        azure_client_secret: typing.Optional[builtins.str] = None,
        azure_environment: typing.Optional[builtins.str] = None,
        azure_login_app_id: typing.Optional[builtins.str] = None,
        azure_tenant_id: typing.Optional[builtins.str] = None,
        azure_use_msi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        azure_workspace_resource_id: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        config_file: typing.Optional[builtins.str] = None,
        databricks_cli_path: typing.Optional[builtins.str] = None,
        databricks_id_token_filepath: typing.Optional[builtins.str] = None,
        debug_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        debug_truncate_bytes: typing.Optional[jsii.Number] = None,
        google_credentials: typing.Optional[builtins.str] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        http_timeout_seconds: typing.Optional[jsii.Number] = None,
        metadata_service_url: typing.Optional[builtins.str] = None,
        oauth_callback_port: typing.Optional[jsii.Number] = None,
        oidc_token_env: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
        retry_timeout_seconds: typing.Optional[jsii.Number] = None,
        serverless_compute_id: typing.Optional[builtins.str] = None,
        skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs databricks} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#account_id DatabricksProvider#account_id}.
        :param actions_id_token_request_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_token DatabricksProvider#actions_id_token_request_token}.
        :param actions_id_token_request_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_url DatabricksProvider#actions_id_token_request_url}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#alias DatabricksProvider#alias}
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#audience DatabricksProvider#audience}.
        :param auth_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#auth_type DatabricksProvider#auth_type}.
        :param azure_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_id DatabricksProvider#azure_client_id}.
        :param azure_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_secret DatabricksProvider#azure_client_secret}.
        :param azure_environment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_environment DatabricksProvider#azure_environment}.
        :param azure_login_app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_login_app_id DatabricksProvider#azure_login_app_id}.
        :param azure_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_tenant_id DatabricksProvider#azure_tenant_id}.
        :param azure_use_msi: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_use_msi DatabricksProvider#azure_use_msi}.
        :param azure_workspace_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_workspace_resource_id DatabricksProvider#azure_workspace_resource_id}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_id DatabricksProvider#client_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_secret DatabricksProvider#client_secret}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#cluster_id DatabricksProvider#cluster_id}.
        :param config_file: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#config_file DatabricksProvider#config_file}.
        :param databricks_cli_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_cli_path DatabricksProvider#databricks_cli_path}.
        :param databricks_id_token_filepath: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_id_token_filepath DatabricksProvider#databricks_id_token_filepath}.
        :param debug_headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_headers DatabricksProvider#debug_headers}.
        :param debug_truncate_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_truncate_bytes DatabricksProvider#debug_truncate_bytes}.
        :param google_credentials: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_credentials DatabricksProvider#google_credentials}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_service_account DatabricksProvider#google_service_account}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#host DatabricksProvider#host}.
        :param http_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#http_timeout_seconds DatabricksProvider#http_timeout_seconds}.
        :param metadata_service_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#metadata_service_url DatabricksProvider#metadata_service_url}.
        :param oauth_callback_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oauth_callback_port DatabricksProvider#oauth_callback_port}.
        :param oidc_token_env: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oidc_token_env DatabricksProvider#oidc_token_env}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#password DatabricksProvider#password}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#profile DatabricksProvider#profile}.
        :param rate_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#rate_limit DatabricksProvider#rate_limit}.
        :param retry_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#retry_timeout_seconds DatabricksProvider#retry_timeout_seconds}.
        :param serverless_compute_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#serverless_compute_id DatabricksProvider#serverless_compute_id}.
        :param skip_verify: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#skip_verify DatabricksProvider#skip_verify}.
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#token DatabricksProvider#token}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#username DatabricksProvider#username}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#warehouse_id DatabricksProvider#warehouse_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a36c6b5c64a7527dee4a05b45f65060153125c14e35a081e91ec19023d45d1dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DatabricksProviderConfig(
            account_id=account_id,
            actions_id_token_request_token=actions_id_token_request_token,
            actions_id_token_request_url=actions_id_token_request_url,
            alias=alias,
            audience=audience,
            auth_type=auth_type,
            azure_client_id=azure_client_id,
            azure_client_secret=azure_client_secret,
            azure_environment=azure_environment,
            azure_login_app_id=azure_login_app_id,
            azure_tenant_id=azure_tenant_id,
            azure_use_msi=azure_use_msi,
            azure_workspace_resource_id=azure_workspace_resource_id,
            client_id=client_id,
            client_secret=client_secret,
            cluster_id=cluster_id,
            config_file=config_file,
            databricks_cli_path=databricks_cli_path,
            databricks_id_token_filepath=databricks_id_token_filepath,
            debug_headers=debug_headers,
            debug_truncate_bytes=debug_truncate_bytes,
            google_credentials=google_credentials,
            google_service_account=google_service_account,
            host=host,
            http_timeout_seconds=http_timeout_seconds,
            metadata_service_url=metadata_service_url,
            oauth_callback_port=oauth_callback_port,
            oidc_token_env=oidc_token_env,
            password=password,
            profile=profile,
            rate_limit=rate_limit,
            retry_timeout_seconds=retry_timeout_seconds,
            serverless_compute_id=serverless_compute_id,
            skip_verify=skip_verify,
            token=token,
            username=username,
            warehouse_id=warehouse_id,
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
        '''Generates CDKTF code for importing a DatabricksProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabricksProvider to import.
        :param import_from_id: The id of the existing DatabricksProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabricksProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2d68acb8c2d4800de49f2da0f9ab03fa71956582dfe3d63cd3c084785a4f785)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetActionsIdTokenRequestToken")
    def reset_actions_id_token_request_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionsIdTokenRequestToken", []))

    @jsii.member(jsii_name="resetActionsIdTokenRequestUrl")
    def reset_actions_id_token_request_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionsIdTokenRequestUrl", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetAzureClientId")
    def reset_azure_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureClientId", []))

    @jsii.member(jsii_name="resetAzureClientSecret")
    def reset_azure_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureClientSecret", []))

    @jsii.member(jsii_name="resetAzureEnvironment")
    def reset_azure_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureEnvironment", []))

    @jsii.member(jsii_name="resetAzureLoginAppId")
    def reset_azure_login_app_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureLoginAppId", []))

    @jsii.member(jsii_name="resetAzureTenantId")
    def reset_azure_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureTenantId", []))

    @jsii.member(jsii_name="resetAzureUseMsi")
    def reset_azure_use_msi(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureUseMsi", []))

    @jsii.member(jsii_name="resetAzureWorkspaceResourceId")
    def reset_azure_workspace_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureWorkspaceResourceId", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetConfigFile")
    def reset_config_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigFile", []))

    @jsii.member(jsii_name="resetDatabricksCliPath")
    def reset_databricks_cli_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksCliPath", []))

    @jsii.member(jsii_name="resetDatabricksIdTokenFilepath")
    def reset_databricks_id_token_filepath(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksIdTokenFilepath", []))

    @jsii.member(jsii_name="resetDebugHeaders")
    def reset_debug_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDebugHeaders", []))

    @jsii.member(jsii_name="resetDebugTruncateBytes")
    def reset_debug_truncate_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDebugTruncateBytes", []))

    @jsii.member(jsii_name="resetGoogleCredentials")
    def reset_google_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleCredentials", []))

    @jsii.member(jsii_name="resetGoogleServiceAccount")
    def reset_google_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleServiceAccount", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetHttpTimeoutSeconds")
    def reset_http_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpTimeoutSeconds", []))

    @jsii.member(jsii_name="resetMetadataServiceUrl")
    def reset_metadata_service_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadataServiceUrl", []))

    @jsii.member(jsii_name="resetOauthCallbackPort")
    def reset_oauth_callback_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthCallbackPort", []))

    @jsii.member(jsii_name="resetOidcTokenEnv")
    def reset_oidc_token_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcTokenEnv", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetRateLimit")
    def reset_rate_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateLimit", []))

    @jsii.member(jsii_name="resetRetryTimeoutSeconds")
    def reset_retry_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryTimeoutSeconds", []))

    @jsii.member(jsii_name="resetServerlessComputeId")
    def reset_serverless_compute_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerlessComputeId", []))

    @jsii.member(jsii_name="resetSkipVerify")
    def reset_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipVerify", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetWarehouseId")
    def reset_warehouse_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWarehouseId", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="actionsIdTokenRequestTokenInput")
    def actions_id_token_request_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionsIdTokenRequestTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="actionsIdTokenRequestUrlInput")
    def actions_id_token_request_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionsIdTokenRequestUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="azureClientIdInput")
    def azure_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureClientSecretInput")
    def azure_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="azureEnvironmentInput")
    def azure_environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureEnvironmentInput"))

    @builtins.property
    @jsii.member(jsii_name="azureLoginAppIdInput")
    def azure_login_app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureLoginAppIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureTenantIdInput")
    def azure_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureUseMsiInput")
    def azure_use_msi_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "azureUseMsiInput"))

    @builtins.property
    @jsii.member(jsii_name="azureWorkspaceResourceIdInput")
    def azure_workspace_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureWorkspaceResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configFileInput")
    def config_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configFileInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksCliPathInput")
    def databricks_cli_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksCliPathInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksIdTokenFilepathInput")
    def databricks_id_token_filepath_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksIdTokenFilepathInput"))

    @builtins.property
    @jsii.member(jsii_name="debugHeadersInput")
    def debug_headers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "debugHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="debugTruncateBytesInput")
    def debug_truncate_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "debugTruncateBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="googleCredentialsInput")
    def google_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleCredentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccountInput")
    def google_service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="httpTimeoutSecondsInput")
    def http_timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpTimeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataServiceUrlInput")
    def metadata_service_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataServiceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthCallbackPortInput")
    def oauth_callback_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oauthCallbackPortInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcTokenEnvInput")
    def oidc_token_env_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcTokenEnvInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitInput")
    def rate_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rateLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="retryTimeoutSecondsInput")
    def retry_timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryTimeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="serverlessComputeIdInput")
    def serverless_compute_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverlessComputeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="skipVerifyInput")
    def skip_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="warehouseIdInput")
    def warehouse_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad7b47a2ce2be69c4cc68606bbb0b41c7cf41c2a6d803eb6918276e31494a18c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="actionsIdTokenRequestToken")
    def actions_id_token_request_token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionsIdTokenRequestToken"))

    @actions_id_token_request_token.setter
    def actions_id_token_request_token(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c63ef137b245efa2dd2b9fd7f21cfab92d76368ab8a9fdd086f0641779fd0f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionsIdTokenRequestToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="actionsIdTokenRequestUrl")
    def actions_id_token_request_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionsIdTokenRequestUrl"))

    @actions_id_token_request_url.setter
    def actions_id_token_request_url(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a02560d2ae90417ffd99b6a30423ac8ad8494e89ceb732ca6f84540970b57c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionsIdTokenRequestUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3dab5e6f10725727de11c66c61284bd1d96804464fc4378aa5088a0368fc859)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__893c6f72c3f981a1a596cc306b8b318bed514216b2dd970177b6ef0ad3bacc7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc9cca6a1fdb6e4b10d2a2cb7b80f31152cd472c4eaf70bc8dea6dfb0302e523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureClientId")
    def azure_client_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientId"))

    @azure_client_id.setter
    def azure_client_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4c77e8b508f9c46f78cf5d200c9cfb8786a53399d492dfc486089f50c7965b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureClientSecret")
    def azure_client_secret(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientSecret"))

    @azure_client_secret.setter
    def azure_client_secret(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__811afe1742234431c1ac6bdf3c4410a793e638ec51b0af7e2205a30a9838f61c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureEnvironment")
    def azure_environment(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureEnvironment"))

    @azure_environment.setter
    def azure_environment(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cbfd58fb5dae84b74a360e7be035bb15a542145cf8f68f18c4faf76e97cc104)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureLoginAppId")
    def azure_login_app_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureLoginAppId"))

    @azure_login_app_id.setter
    def azure_login_app_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1274a61c4a0dcfa9ade53c3481ccf4b88eee156dcbf530ddf399dea4dff4ecd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureLoginAppId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureTenantId")
    def azure_tenant_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureTenantId"))

    @azure_tenant_id.setter
    def azure_tenant_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea357ba4fffacd244f5693345857b47bab7cd161237f987aaad2d33a4586b6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureTenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureUseMsi")
    def azure_use_msi(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "azureUseMsi"))

    @azure_use_msi.setter
    def azure_use_msi(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__854eace2e88d7c8bc6e94cc5a89e1e430f9613da8083d1cdfa095c0b08b9471e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureUseMsi", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureWorkspaceResourceId")
    def azure_workspace_resource_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureWorkspaceResourceId"))

    @azure_workspace_resource_id.setter
    def azure_workspace_resource_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f921774bd7572da7c73ecb50b299e0920406df3759671ba3c3b03c4c2d64b4be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureWorkspaceResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb3d6e4d1f1d4329b94a556a55143cca5baf8e0e08417025081edb7b5dfe5825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1bb226c30e437dc0d8606a52bb0b649676f71591e883241e8349a8a4267093f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9e241189c58eb9a6affa7de9dfbacf22e5048d3842214dc172e11e50b8549a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configFile")
    def config_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configFile"))

    @config_file.setter
    def config_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7abe31c8600033142c6d32200bd8a0d8dc601d960cb1b7799404a6206dfa2ce5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksCliPath")
    def databricks_cli_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksCliPath"))

    @databricks_cli_path.setter
    def databricks_cli_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__843205206dfb8e4f3e8267a807432ed0be6ee7e72becbd915dce4125b8364dc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksCliPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databricksIdTokenFilepath")
    def databricks_id_token_filepath(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databricksIdTokenFilepath"))

    @databricks_id_token_filepath.setter
    def databricks_id_token_filepath(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5c0a5afbef70b5a822d8e8942f126a21f01a2faa34840d2d8f7e1259f0bb911)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databricksIdTokenFilepath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="debugHeaders")
    def debug_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "debugHeaders"))

    @debug_headers.setter
    def debug_headers(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__023d5963132db7eb7cb06c7a27f450156d8772362bd34c4b20ba3c44b747f6ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "debugHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="debugTruncateBytes")
    def debug_truncate_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "debugTruncateBytes"))

    @debug_truncate_bytes.setter
    def debug_truncate_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74da7e67d20448ebb559021f5899036e416ce8d1efc4fcf8469519c2be79f787)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "debugTruncateBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleCredentials")
    def google_credentials(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleCredentials"))

    @google_credentials.setter
    def google_credentials(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcaa2c0772bdcca2b37c15ca99710837ca4df8e8f8638cdded87d6cc5c49c633)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleCredentials", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccount")
    def google_service_account(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleServiceAccount"))

    @google_service_account.setter
    def google_service_account(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5752990ad0b991deef42e62d61b2fb47341355be8cbb50c25d8cf0f5c9318da4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleServiceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e10310abaff56697b33f89a76ac43107fe815dafe5db49599113526a0041a7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpTimeoutSeconds")
    def http_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpTimeoutSeconds"))

    @http_timeout_seconds.setter
    def http_timeout_seconds(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81d169ff2ff1974e491de4da7daf98fdbd54bdfaa5f77a74dd1051bcd4e78b37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpTimeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadataServiceUrl")
    def metadata_service_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataServiceUrl"))

    @metadata_service_url.setter
    def metadata_service_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec9bf448a36925b01556edfae6e182259702a543fabec7ca690c168328e996c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadataServiceUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oauthCallbackPort")
    def oauth_callback_port(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oauthCallbackPort"))

    @oauth_callback_port.setter
    def oauth_callback_port(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530cd05ebc3e1cde5bb99b8dad7c68c02781ad5289a2f6339c8b2f96f96bad02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oauthCallbackPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcTokenEnv")
    def oidc_token_env(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcTokenEnv"))

    @oidc_token_env.setter
    def oidc_token_env(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f6da9645388a2b371ce586c393e05fd164597d09e8c86cfb376c9ec9c74d02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcTokenEnv", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb6489f91725b35b690266d0aba1d034c02a1f2093c9e225404e01895dd3f12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d4a000b74c231b9fc2c51d2dd5b632d98639e22400ee2272262dc66480131f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rateLimit")
    def rate_limit(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rateLimit"))

    @rate_limit.setter
    def rate_limit(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543036029c1933258eaf8fe646e164af1918021fef3239f63ce76af3f8b3e973)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rateLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryTimeoutSeconds")
    def retry_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryTimeoutSeconds"))

    @retry_timeout_seconds.setter
    def retry_timeout_seconds(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc84220a559aca3adc9ccd6597dcd3416fa18f165937c639524a504ded0f079c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryTimeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverlessComputeId")
    def serverless_compute_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverlessComputeId"))

    @serverless_compute_id.setter
    def serverless_compute_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331f2ba0527f66ba82dca5fd8d01eebc868d26012746986c5788f69ace42dc99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverlessComputeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipVerify")
    def skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipVerify"))

    @skip_verify.setter
    def skip_verify(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d84c2f86add543980d247bc39dd0b58e48232cd7ff73a910ef3d7d9986fc954)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7754ab0a83a8b274b0819af27d27962efb5c31653ce4de1d124a85c9d0d49691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e69e1ae573766228c1a1882788e8c63333851f88d075174784c335247be9f2bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warehouseId")
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warehouseId"))

    @warehouse_id.setter
    def warehouse_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3451ad63102bd66fa6899d830f2f8f0bd432ee3aa9bc23dafd25ef2324b5f90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warehouseId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.provider.DatabricksProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "actions_id_token_request_token": "actionsIdTokenRequestToken",
        "actions_id_token_request_url": "actionsIdTokenRequestUrl",
        "alias": "alias",
        "audience": "audience",
        "auth_type": "authType",
        "azure_client_id": "azureClientId",
        "azure_client_secret": "azureClientSecret",
        "azure_environment": "azureEnvironment",
        "azure_login_app_id": "azureLoginAppId",
        "azure_tenant_id": "azureTenantId",
        "azure_use_msi": "azureUseMsi",
        "azure_workspace_resource_id": "azureWorkspaceResourceId",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "cluster_id": "clusterId",
        "config_file": "configFile",
        "databricks_cli_path": "databricksCliPath",
        "databricks_id_token_filepath": "databricksIdTokenFilepath",
        "debug_headers": "debugHeaders",
        "debug_truncate_bytes": "debugTruncateBytes",
        "google_credentials": "googleCredentials",
        "google_service_account": "googleServiceAccount",
        "host": "host",
        "http_timeout_seconds": "httpTimeoutSeconds",
        "metadata_service_url": "metadataServiceUrl",
        "oauth_callback_port": "oauthCallbackPort",
        "oidc_token_env": "oidcTokenEnv",
        "password": "password",
        "profile": "profile",
        "rate_limit": "rateLimit",
        "retry_timeout_seconds": "retryTimeoutSeconds",
        "serverless_compute_id": "serverlessComputeId",
        "skip_verify": "skipVerify",
        "token": "token",
        "username": "username",
        "warehouse_id": "warehouseId",
    },
)
class DatabricksProviderConfig:
    def __init__(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        actions_id_token_request_token: typing.Optional[builtins.str] = None,
        actions_id_token_request_url: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        audience: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        azure_client_id: typing.Optional[builtins.str] = None,
        azure_client_secret: typing.Optional[builtins.str] = None,
        azure_environment: typing.Optional[builtins.str] = None,
        azure_login_app_id: typing.Optional[builtins.str] = None,
        azure_tenant_id: typing.Optional[builtins.str] = None,
        azure_use_msi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        azure_workspace_resource_id: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        config_file: typing.Optional[builtins.str] = None,
        databricks_cli_path: typing.Optional[builtins.str] = None,
        databricks_id_token_filepath: typing.Optional[builtins.str] = None,
        debug_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        debug_truncate_bytes: typing.Optional[jsii.Number] = None,
        google_credentials: typing.Optional[builtins.str] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        http_timeout_seconds: typing.Optional[jsii.Number] = None,
        metadata_service_url: typing.Optional[builtins.str] = None,
        oauth_callback_port: typing.Optional[jsii.Number] = None,
        oidc_token_env: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
        retry_timeout_seconds: typing.Optional[jsii.Number] = None,
        serverless_compute_id: typing.Optional[builtins.str] = None,
        skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        warehouse_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#account_id DatabricksProvider#account_id}.
        :param actions_id_token_request_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_token DatabricksProvider#actions_id_token_request_token}.
        :param actions_id_token_request_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_url DatabricksProvider#actions_id_token_request_url}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#alias DatabricksProvider#alias}
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#audience DatabricksProvider#audience}.
        :param auth_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#auth_type DatabricksProvider#auth_type}.
        :param azure_client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_id DatabricksProvider#azure_client_id}.
        :param azure_client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_secret DatabricksProvider#azure_client_secret}.
        :param azure_environment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_environment DatabricksProvider#azure_environment}.
        :param azure_login_app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_login_app_id DatabricksProvider#azure_login_app_id}.
        :param azure_tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_tenant_id DatabricksProvider#azure_tenant_id}.
        :param azure_use_msi: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_use_msi DatabricksProvider#azure_use_msi}.
        :param azure_workspace_resource_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_workspace_resource_id DatabricksProvider#azure_workspace_resource_id}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_id DatabricksProvider#client_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_secret DatabricksProvider#client_secret}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#cluster_id DatabricksProvider#cluster_id}.
        :param config_file: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#config_file DatabricksProvider#config_file}.
        :param databricks_cli_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_cli_path DatabricksProvider#databricks_cli_path}.
        :param databricks_id_token_filepath: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_id_token_filepath DatabricksProvider#databricks_id_token_filepath}.
        :param debug_headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_headers DatabricksProvider#debug_headers}.
        :param debug_truncate_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_truncate_bytes DatabricksProvider#debug_truncate_bytes}.
        :param google_credentials: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_credentials DatabricksProvider#google_credentials}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_service_account DatabricksProvider#google_service_account}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#host DatabricksProvider#host}.
        :param http_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#http_timeout_seconds DatabricksProvider#http_timeout_seconds}.
        :param metadata_service_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#metadata_service_url DatabricksProvider#metadata_service_url}.
        :param oauth_callback_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oauth_callback_port DatabricksProvider#oauth_callback_port}.
        :param oidc_token_env: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oidc_token_env DatabricksProvider#oidc_token_env}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#password DatabricksProvider#password}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#profile DatabricksProvider#profile}.
        :param rate_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#rate_limit DatabricksProvider#rate_limit}.
        :param retry_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#retry_timeout_seconds DatabricksProvider#retry_timeout_seconds}.
        :param serverless_compute_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#serverless_compute_id DatabricksProvider#serverless_compute_id}.
        :param skip_verify: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#skip_verify DatabricksProvider#skip_verify}.
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#token DatabricksProvider#token}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#username DatabricksProvider#username}.
        :param warehouse_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#warehouse_id DatabricksProvider#warehouse_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d68062a3e12880da6b3c971827e3ab8ce6e8c830e6f01e46f0ff4a366073157)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument actions_id_token_request_token", value=actions_id_token_request_token, expected_type=type_hints["actions_id_token_request_token"])
            check_type(argname="argument actions_id_token_request_url", value=actions_id_token_request_url, expected_type=type_hints["actions_id_token_request_url"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument azure_client_id", value=azure_client_id, expected_type=type_hints["azure_client_id"])
            check_type(argname="argument azure_client_secret", value=azure_client_secret, expected_type=type_hints["azure_client_secret"])
            check_type(argname="argument azure_environment", value=azure_environment, expected_type=type_hints["azure_environment"])
            check_type(argname="argument azure_login_app_id", value=azure_login_app_id, expected_type=type_hints["azure_login_app_id"])
            check_type(argname="argument azure_tenant_id", value=azure_tenant_id, expected_type=type_hints["azure_tenant_id"])
            check_type(argname="argument azure_use_msi", value=azure_use_msi, expected_type=type_hints["azure_use_msi"])
            check_type(argname="argument azure_workspace_resource_id", value=azure_workspace_resource_id, expected_type=type_hints["azure_workspace_resource_id"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument config_file", value=config_file, expected_type=type_hints["config_file"])
            check_type(argname="argument databricks_cli_path", value=databricks_cli_path, expected_type=type_hints["databricks_cli_path"])
            check_type(argname="argument databricks_id_token_filepath", value=databricks_id_token_filepath, expected_type=type_hints["databricks_id_token_filepath"])
            check_type(argname="argument debug_headers", value=debug_headers, expected_type=type_hints["debug_headers"])
            check_type(argname="argument debug_truncate_bytes", value=debug_truncate_bytes, expected_type=type_hints["debug_truncate_bytes"])
            check_type(argname="argument google_credentials", value=google_credentials, expected_type=type_hints["google_credentials"])
            check_type(argname="argument google_service_account", value=google_service_account, expected_type=type_hints["google_service_account"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument http_timeout_seconds", value=http_timeout_seconds, expected_type=type_hints["http_timeout_seconds"])
            check_type(argname="argument metadata_service_url", value=metadata_service_url, expected_type=type_hints["metadata_service_url"])
            check_type(argname="argument oauth_callback_port", value=oauth_callback_port, expected_type=type_hints["oauth_callback_port"])
            check_type(argname="argument oidc_token_env", value=oidc_token_env, expected_type=type_hints["oidc_token_env"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument rate_limit", value=rate_limit, expected_type=type_hints["rate_limit"])
            check_type(argname="argument retry_timeout_seconds", value=retry_timeout_seconds, expected_type=type_hints["retry_timeout_seconds"])
            check_type(argname="argument serverless_compute_id", value=serverless_compute_id, expected_type=type_hints["serverless_compute_id"])
            check_type(argname="argument skip_verify", value=skip_verify, expected_type=type_hints["skip_verify"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument warehouse_id", value=warehouse_id, expected_type=type_hints["warehouse_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account_id is not None:
            self._values["account_id"] = account_id
        if actions_id_token_request_token is not None:
            self._values["actions_id_token_request_token"] = actions_id_token_request_token
        if actions_id_token_request_url is not None:
            self._values["actions_id_token_request_url"] = actions_id_token_request_url
        if alias is not None:
            self._values["alias"] = alias
        if audience is not None:
            self._values["audience"] = audience
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if azure_client_id is not None:
            self._values["azure_client_id"] = azure_client_id
        if azure_client_secret is not None:
            self._values["azure_client_secret"] = azure_client_secret
        if azure_environment is not None:
            self._values["azure_environment"] = azure_environment
        if azure_login_app_id is not None:
            self._values["azure_login_app_id"] = azure_login_app_id
        if azure_tenant_id is not None:
            self._values["azure_tenant_id"] = azure_tenant_id
        if azure_use_msi is not None:
            self._values["azure_use_msi"] = azure_use_msi
        if azure_workspace_resource_id is not None:
            self._values["azure_workspace_resource_id"] = azure_workspace_resource_id
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if config_file is not None:
            self._values["config_file"] = config_file
        if databricks_cli_path is not None:
            self._values["databricks_cli_path"] = databricks_cli_path
        if databricks_id_token_filepath is not None:
            self._values["databricks_id_token_filepath"] = databricks_id_token_filepath
        if debug_headers is not None:
            self._values["debug_headers"] = debug_headers
        if debug_truncate_bytes is not None:
            self._values["debug_truncate_bytes"] = debug_truncate_bytes
        if google_credentials is not None:
            self._values["google_credentials"] = google_credentials
        if google_service_account is not None:
            self._values["google_service_account"] = google_service_account
        if host is not None:
            self._values["host"] = host
        if http_timeout_seconds is not None:
            self._values["http_timeout_seconds"] = http_timeout_seconds
        if metadata_service_url is not None:
            self._values["metadata_service_url"] = metadata_service_url
        if oauth_callback_port is not None:
            self._values["oauth_callback_port"] = oauth_callback_port
        if oidc_token_env is not None:
            self._values["oidc_token_env"] = oidc_token_env
        if password is not None:
            self._values["password"] = password
        if profile is not None:
            self._values["profile"] = profile
        if rate_limit is not None:
            self._values["rate_limit"] = rate_limit
        if retry_timeout_seconds is not None:
            self._values["retry_timeout_seconds"] = retry_timeout_seconds
        if serverless_compute_id is not None:
            self._values["serverless_compute_id"] = serverless_compute_id
        if skip_verify is not None:
            self._values["skip_verify"] = skip_verify
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username
        if warehouse_id is not None:
            self._values["warehouse_id"] = warehouse_id

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#account_id DatabricksProvider#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def actions_id_token_request_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_token DatabricksProvider#actions_id_token_request_token}.'''
        result = self._values.get("actions_id_token_request_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def actions_id_token_request_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#actions_id_token_request_url DatabricksProvider#actions_id_token_request_url}.'''
        result = self._values.get("actions_id_token_request_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#alias DatabricksProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#audience DatabricksProvider#audience}.'''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#auth_type DatabricksProvider#auth_type}.'''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_id DatabricksProvider#azure_client_id}.'''
        result = self._values.get("azure_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_client_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_client_secret DatabricksProvider#azure_client_secret}.'''
        result = self._values.get("azure_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_environment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_environment DatabricksProvider#azure_environment}.'''
        result = self._values.get("azure_environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_login_app_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_login_app_id DatabricksProvider#azure_login_app_id}.'''
        result = self._values.get("azure_login_app_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_tenant_id DatabricksProvider#azure_tenant_id}.'''
        result = self._values.get("azure_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_use_msi(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_use_msi DatabricksProvider#azure_use_msi}.'''
        result = self._values.get("azure_use_msi")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def azure_workspace_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#azure_workspace_resource_id DatabricksProvider#azure_workspace_resource_id}.'''
        result = self._values.get("azure_workspace_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_id DatabricksProvider#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#client_secret DatabricksProvider#client_secret}.'''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#cluster_id DatabricksProvider#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#config_file DatabricksProvider#config_file}.'''
        result = self._values.get("config_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_cli_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_cli_path DatabricksProvider#databricks_cli_path}.'''
        result = self._values.get("databricks_cli_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_id_token_filepath(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#databricks_id_token_filepath DatabricksProvider#databricks_id_token_filepath}.'''
        result = self._values.get("databricks_id_token_filepath")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def debug_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_headers DatabricksProvider#debug_headers}.'''
        result = self._values.get("debug_headers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def debug_truncate_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#debug_truncate_bytes DatabricksProvider#debug_truncate_bytes}.'''
        result = self._values.get("debug_truncate_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def google_credentials(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_credentials DatabricksProvider#google_credentials}.'''
        result = self._values.get("google_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def google_service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#google_service_account DatabricksProvider#google_service_account}.'''
        result = self._values.get("google_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#host DatabricksProvider#host}.'''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#http_timeout_seconds DatabricksProvider#http_timeout_seconds}.'''
        result = self._values.get("http_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metadata_service_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#metadata_service_url DatabricksProvider#metadata_service_url}.'''
        result = self._values.get("metadata_service_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_callback_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oauth_callback_port DatabricksProvider#oauth_callback_port}.'''
        result = self._values.get("oauth_callback_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oidc_token_env(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#oidc_token_env DatabricksProvider#oidc_token_env}.'''
        result = self._values.get("oidc_token_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#password DatabricksProvider#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#profile DatabricksProvider#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rate_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#rate_limit DatabricksProvider#rate_limit}.'''
        result = self._values.get("rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#retry_timeout_seconds DatabricksProvider#retry_timeout_seconds}.'''
        result = self._values.get("retry_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def serverless_compute_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#serverless_compute_id DatabricksProvider#serverless_compute_id}.'''
        result = self._values.get("serverless_compute_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#skip_verify DatabricksProvider#skip_verify}.'''
        result = self._values.get("skip_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#token DatabricksProvider#token}.'''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#username DatabricksProvider#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def warehouse_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs#warehouse_id DatabricksProvider#warehouse_id}.'''
        result = self._values.get("warehouse_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabricksProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabricksProvider",
    "DatabricksProviderConfig",
]

publication.publish()

def _typecheckingstub__a36c6b5c64a7527dee4a05b45f65060153125c14e35a081e91ec19023d45d1dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: typing.Optional[builtins.str] = None,
    actions_id_token_request_token: typing.Optional[builtins.str] = None,
    actions_id_token_request_url: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    audience: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    azure_client_id: typing.Optional[builtins.str] = None,
    azure_client_secret: typing.Optional[builtins.str] = None,
    azure_environment: typing.Optional[builtins.str] = None,
    azure_login_app_id: typing.Optional[builtins.str] = None,
    azure_tenant_id: typing.Optional[builtins.str] = None,
    azure_use_msi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    azure_workspace_resource_id: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    config_file: typing.Optional[builtins.str] = None,
    databricks_cli_path: typing.Optional[builtins.str] = None,
    databricks_id_token_filepath: typing.Optional[builtins.str] = None,
    debug_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    debug_truncate_bytes: typing.Optional[jsii.Number] = None,
    google_credentials: typing.Optional[builtins.str] = None,
    google_service_account: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    http_timeout_seconds: typing.Optional[jsii.Number] = None,
    metadata_service_url: typing.Optional[builtins.str] = None,
    oauth_callback_port: typing.Optional[jsii.Number] = None,
    oidc_token_env: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    profile: typing.Optional[builtins.str] = None,
    rate_limit: typing.Optional[jsii.Number] = None,
    retry_timeout_seconds: typing.Optional[jsii.Number] = None,
    serverless_compute_id: typing.Optional[builtins.str] = None,
    skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2d68acb8c2d4800de49f2da0f9ab03fa71956582dfe3d63cd3c084785a4f785(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad7b47a2ce2be69c4cc68606bbb0b41c7cf41c2a6d803eb6918276e31494a18c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c63ef137b245efa2dd2b9fd7f21cfab92d76368ab8a9fdd086f0641779fd0f7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a02560d2ae90417ffd99b6a30423ac8ad8494e89ceb732ca6f84540970b57c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3dab5e6f10725727de11c66c61284bd1d96804464fc4378aa5088a0368fc859(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893c6f72c3f981a1a596cc306b8b318bed514216b2dd970177b6ef0ad3bacc7b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc9cca6a1fdb6e4b10d2a2cb7b80f31152cd472c4eaf70bc8dea6dfb0302e523(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4c77e8b508f9c46f78cf5d200c9cfb8786a53399d492dfc486089f50c7965b2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811afe1742234431c1ac6bdf3c4410a793e638ec51b0af7e2205a30a9838f61c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cbfd58fb5dae84b74a360e7be035bb15a542145cf8f68f18c4faf76e97cc104(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1274a61c4a0dcfa9ade53c3481ccf4b88eee156dcbf530ddf399dea4dff4ecd5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea357ba4fffacd244f5693345857b47bab7cd161237f987aaad2d33a4586b6e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__854eace2e88d7c8bc6e94cc5a89e1e430f9613da8083d1cdfa095c0b08b9471e(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f921774bd7572da7c73ecb50b299e0920406df3759671ba3c3b03c4c2d64b4be(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb3d6e4d1f1d4329b94a556a55143cca5baf8e0e08417025081edb7b5dfe5825(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1bb226c30e437dc0d8606a52bb0b649676f71591e883241e8349a8a4267093f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9e241189c58eb9a6affa7de9dfbacf22e5048d3842214dc172e11e50b8549a3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7abe31c8600033142c6d32200bd8a0d8dc601d960cb1b7799404a6206dfa2ce5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__843205206dfb8e4f3e8267a807432ed0be6ee7e72becbd915dce4125b8364dc0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5c0a5afbef70b5a822d8e8942f126a21f01a2faa34840d2d8f7e1259f0bb911(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__023d5963132db7eb7cb06c7a27f450156d8772362bd34c4b20ba3c44b747f6ec(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74da7e67d20448ebb559021f5899036e416ce8d1efc4fcf8469519c2be79f787(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcaa2c0772bdcca2b37c15ca99710837ca4df8e8f8638cdded87d6cc5c49c633(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5752990ad0b991deef42e62d61b2fb47341355be8cbb50c25d8cf0f5c9318da4(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e10310abaff56697b33f89a76ac43107fe815dafe5db49599113526a0041a7db(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81d169ff2ff1974e491de4da7daf98fdbd54bdfaa5f77a74dd1051bcd4e78b37(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec9bf448a36925b01556edfae6e182259702a543fabec7ca690c168328e996c6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530cd05ebc3e1cde5bb99b8dad7c68c02781ad5289a2f6339c8b2f96f96bad02(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f6da9645388a2b371ce586c393e05fd164597d09e8c86cfb376c9ec9c74d02(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb6489f91725b35b690266d0aba1d034c02a1f2093c9e225404e01895dd3f12(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d4a000b74c231b9fc2c51d2dd5b632d98639e22400ee2272262dc66480131f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543036029c1933258eaf8fe646e164af1918021fef3239f63ce76af3f8b3e973(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc84220a559aca3adc9ccd6597dcd3416fa18f165937c639524a504ded0f079c(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331f2ba0527f66ba82dca5fd8d01eebc868d26012746986c5788f69ace42dc99(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d84c2f86add543980d247bc39dd0b58e48232cd7ff73a910ef3d7d9986fc954(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7754ab0a83a8b274b0819af27d27962efb5c31653ce4de1d124a85c9d0d49691(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69e1ae573766228c1a1882788e8c63333851f88d075174784c335247be9f2bc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3451ad63102bd66fa6899d830f2f8f0bd432ee3aa9bc23dafd25ef2324b5f90(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d68062a3e12880da6b3c971827e3ab8ce6e8c830e6f01e46f0ff4a366073157(
    *,
    account_id: typing.Optional[builtins.str] = None,
    actions_id_token_request_token: typing.Optional[builtins.str] = None,
    actions_id_token_request_url: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    audience: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    azure_client_id: typing.Optional[builtins.str] = None,
    azure_client_secret: typing.Optional[builtins.str] = None,
    azure_environment: typing.Optional[builtins.str] = None,
    azure_login_app_id: typing.Optional[builtins.str] = None,
    azure_tenant_id: typing.Optional[builtins.str] = None,
    azure_use_msi: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    azure_workspace_resource_id: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    config_file: typing.Optional[builtins.str] = None,
    databricks_cli_path: typing.Optional[builtins.str] = None,
    databricks_id_token_filepath: typing.Optional[builtins.str] = None,
    debug_headers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    debug_truncate_bytes: typing.Optional[jsii.Number] = None,
    google_credentials: typing.Optional[builtins.str] = None,
    google_service_account: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    http_timeout_seconds: typing.Optional[jsii.Number] = None,
    metadata_service_url: typing.Optional[builtins.str] = None,
    oauth_callback_port: typing.Optional[jsii.Number] = None,
    oidc_token_env: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    profile: typing.Optional[builtins.str] = None,
    rate_limit: typing.Optional[jsii.Number] = None,
    retry_timeout_seconds: typing.Optional[jsii.Number] = None,
    serverless_compute_id: typing.Optional[builtins.str] = None,
    skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    warehouse_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
