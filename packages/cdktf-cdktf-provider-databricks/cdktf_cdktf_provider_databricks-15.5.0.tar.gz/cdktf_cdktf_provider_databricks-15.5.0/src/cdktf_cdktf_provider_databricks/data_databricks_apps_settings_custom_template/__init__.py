r'''
# `data_databricks_apps_settings_custom_template`

Refer to the Terraform Registry for docs: [`data_databricks_apps_settings_custom_template`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template).
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


class DataDatabricksAppsSettingsCustomTemplate(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplate",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template databricks_apps_settings_custom_template}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        git_provider: builtins.str,
        git_repo: builtins.str,
        manifest: typing.Union["DataDatabricksAppsSettingsCustomTemplateManifest", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        path: builtins.str,
        description: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template databricks_apps_settings_custom_template} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param git_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_provider DataDatabricksAppsSettingsCustomTemplate#git_provider}.
        :param git_repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_repo DataDatabricksAppsSettingsCustomTemplate#git_repo}.
        :param manifest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#manifest DataDatabricksAppsSettingsCustomTemplate#manifest}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#path DataDatabricksAppsSettingsCustomTemplate#path}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#workspace_id DataDatabricksAppsSettingsCustomTemplate#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0d81d142a96da4e3e838a02f14ceee6d4d0cb17c19637f3ece34eb3558f8aa1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksAppsSettingsCustomTemplateConfig(
            git_provider=git_provider,
            git_repo=git_repo,
            manifest=manifest,
            name=name,
            path=path,
            description=description,
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
        '''Generates CDKTF code for importing a DataDatabricksAppsSettingsCustomTemplate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksAppsSettingsCustomTemplate to import.
        :param import_from_id: The id of the existing DataDatabricksAppsSettingsCustomTemplate that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksAppsSettingsCustomTemplate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9d80a7d70fd5f24b113e4de8acfff9ae24ebc50b6936b65559603409ecf730d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putManifest")
    def put_manifest(
        self,
        *,
        name: builtins.str,
        version: jsii.Number,
        description: typing.Optional[builtins.str] = None,
        resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#version DataDatabricksAppsSettingsCustomTemplate#version}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.
        :param resource_specs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#resource_specs DataDatabricksAppsSettingsCustomTemplate#resource_specs}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifest(
            name=name,
            version=version,
            description=description,
            resource_specs=resource_specs,
        )

        return typing.cast(None, jsii.invoke(self, "putManifest", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="creator")
    def creator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creator"))

    @builtins.property
    @jsii.member(jsii_name="manifest")
    def manifest(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestOutputReference":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestOutputReference", jsii.get(self, "manifest"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="gitProviderInput")
    def git_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="gitRepoInput")
    def git_repo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitRepoInput"))

    @builtins.property
    @jsii.member(jsii_name="manifestInput")
    def manifest_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifest"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifest"]], jsii.get(self, "manifestInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b350a72b857c23731a61f24b3eeb203a8471bf70d539b197bd17f574118f009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitProvider")
    def git_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitProvider"))

    @git_provider.setter
    def git_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cedeba23c59ba2f00d542f7551e0eb7d22b6fe7f2e8dd9d087123fb4748b7fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitRepo")
    def git_repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitRepo"))

    @git_repo.setter
    def git_repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e8eae3ca85def3f172ddc432f15f722ebde0a11e5f9280f5f252508c97df42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitRepo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__179f7056392d6be80199127a25ed5bd02261e2d096a5b2badae03fae0ee36d37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77fe2c516bcf46197751e3fd9e84c4c9595ac8d82a7f315c624ecf338c8c5ecf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf4c02315de4f242bcd106a85fca65d28937f74dbeefa63f08da792ad9037d9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "git_provider": "gitProvider",
        "git_repo": "gitRepo",
        "manifest": "manifest",
        "name": "name",
        "path": "path",
        "description": "description",
        "workspace_id": "workspaceId",
    },
)
class DataDatabricksAppsSettingsCustomTemplateConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        git_provider: builtins.str,
        git_repo: builtins.str,
        manifest: typing.Union["DataDatabricksAppsSettingsCustomTemplateManifest", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        path: builtins.str,
        description: typing.Optional[builtins.str] = None,
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
        :param git_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_provider DataDatabricksAppsSettingsCustomTemplate#git_provider}.
        :param git_repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_repo DataDatabricksAppsSettingsCustomTemplate#git_repo}.
        :param manifest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#manifest DataDatabricksAppsSettingsCustomTemplate#manifest}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#path DataDatabricksAppsSettingsCustomTemplate#path}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#workspace_id DataDatabricksAppsSettingsCustomTemplate#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(manifest, dict):
            manifest = DataDatabricksAppsSettingsCustomTemplateManifest(**manifest)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8febf27efd2fdcf1851081eb22c0b5b6a9373bf8e48adcb0e7d57b1c0fc01f68)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument git_provider", value=git_provider, expected_type=type_hints["git_provider"])
            check_type(argname="argument git_repo", value=git_repo, expected_type=type_hints["git_repo"])
            check_type(argname="argument manifest", value=manifest, expected_type=type_hints["manifest"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "git_provider": git_provider,
            "git_repo": git_repo,
            "manifest": manifest,
            "name": name,
            "path": path,
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
        if description is not None:
            self._values["description"] = description
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
    def git_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_provider DataDatabricksAppsSettingsCustomTemplate#git_provider}.'''
        result = self._values.get("git_provider")
        assert result is not None, "Required property 'git_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def git_repo(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#git_repo DataDatabricksAppsSettingsCustomTemplate#git_repo}.'''
        result = self._values.get("git_repo")
        assert result is not None, "Required property 'git_repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def manifest(self) -> "DataDatabricksAppsSettingsCustomTemplateManifest":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#manifest DataDatabricksAppsSettingsCustomTemplate#manifest}.'''
        result = self._values.get("manifest")
        assert result is not None, "Required property 'manifest' is missing"
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifest", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#path DataDatabricksAppsSettingsCustomTemplate#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#workspace_id DataDatabricksAppsSettingsCustomTemplate#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifest",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "version": "version",
        "description": "description",
        "resource_specs": "resourceSpecs",
    },
)
class DataDatabricksAppsSettingsCustomTemplateManifest:
    def __init__(
        self,
        *,
        name: builtins.str,
        version: jsii.Number,
        description: typing.Optional[builtins.str] = None,
        resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#version DataDatabricksAppsSettingsCustomTemplate#version}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.
        :param resource_specs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#resource_specs DataDatabricksAppsSettingsCustomTemplate#resource_specs}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4842dc41805d24afa739ffb865d04c321187f8ad4e39ee6a8e8a38062dece441)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument resource_specs", value=resource_specs, expected_type=type_hints["resource_specs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "version": version,
        }
        if description is not None:
            self._values["description"] = description
        if resource_specs is not None:
            self._values["resource_specs"] = resource_specs

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#version DataDatabricksAppsSettingsCustomTemplate#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_specs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#resource_specs DataDatabricksAppsSettingsCustomTemplate#resource_specs}.'''
        result = self._values.get("resource_specs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cddcb925a8527553ec13b9ea7a2afb6fb04ffec820ddb8df6360a93afd97f31)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putResourceSpecs")
    def put_resource_specs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c00b32dbdd81157a5d90af8cbf387509bd2ba7b112877c02f4d61cfb51f0fe07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceSpecs", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetResourceSpecs")
    def reset_resource_specs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceSpecs", []))

    @builtins.property
    @jsii.member(jsii_name="resourceSpecs")
    def resource_specs(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsList":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsList", jsii.get(self, "resourceSpecs"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceSpecsInput")
    def resource_specs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs"]]], jsii.get(self, "resourceSpecsInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06f69ec949db29dc6aecee8f46cff69c5902fc6adad27fc979f95bae9ba97255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c39817f447ed72bdbe663d69b87d12803eca2fb4e1363529d7fc4832c4465bb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @version.setter
    def version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff06cc627da6a9cb7003741a3406422711c177f80452228d9174dee09cf34918)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifest]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifest]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed22fe4c87ed255d26b3e22cd9a42ddba1ed4b20e4463a5d842a3ddf4d6fb36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "description": "description",
        "job_spec": "jobSpec",
        "secret_spec": "secretSpec",
        "serving_endpoint_spec": "servingEndpointSpec",
        "sql_warehouse_spec": "sqlWarehouseSpec",
        "uc_securable_spec": "ucSecurableSpec",
    },
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        job_spec: typing.Optional[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        secret_spec: typing.Optional[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        serving_endpoint_spec: typing.Optional[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_warehouse_spec: typing.Optional[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        uc_securable_spec: typing.Optional[typing.Union["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.
        :param job_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#job_spec DataDatabricksAppsSettingsCustomTemplate#job_spec}.
        :param secret_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#secret_spec DataDatabricksAppsSettingsCustomTemplate#secret_spec}.
        :param serving_endpoint_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#serving_endpoint_spec DataDatabricksAppsSettingsCustomTemplate#serving_endpoint_spec}.
        :param sql_warehouse_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#sql_warehouse_spec DataDatabricksAppsSettingsCustomTemplate#sql_warehouse_spec}.
        :param uc_securable_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#uc_securable_spec DataDatabricksAppsSettingsCustomTemplate#uc_securable_spec}.
        '''
        if isinstance(job_spec, dict):
            job_spec = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec(**job_spec)
        if isinstance(secret_spec, dict):
            secret_spec = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(**secret_spec)
        if isinstance(serving_endpoint_spec, dict):
            serving_endpoint_spec = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(**serving_endpoint_spec)
        if isinstance(sql_warehouse_spec, dict):
            sql_warehouse_spec = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(**sql_warehouse_spec)
        if isinstance(uc_securable_spec, dict):
            uc_securable_spec = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(**uc_securable_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4952cf4d3ed7e4ef8aea351699e2b41a111aaf2c905ac6092d3c800402bd94f)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument job_spec", value=job_spec, expected_type=type_hints["job_spec"])
            check_type(argname="argument secret_spec", value=secret_spec, expected_type=type_hints["secret_spec"])
            check_type(argname="argument serving_endpoint_spec", value=serving_endpoint_spec, expected_type=type_hints["serving_endpoint_spec"])
            check_type(argname="argument sql_warehouse_spec", value=sql_warehouse_spec, expected_type=type_hints["sql_warehouse_spec"])
            check_type(argname="argument uc_securable_spec", value=uc_securable_spec, expected_type=type_hints["uc_securable_spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if job_spec is not None:
            self._values["job_spec"] = job_spec
        if secret_spec is not None:
            self._values["secret_spec"] = secret_spec
        if serving_endpoint_spec is not None:
            self._values["serving_endpoint_spec"] = serving_endpoint_spec
        if sql_warehouse_spec is not None:
            self._values["sql_warehouse_spec"] = sql_warehouse_spec
        if uc_securable_spec is not None:
            self._values["uc_securable_spec"] = uc_securable_spec

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#name DataDatabricksAppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#description DataDatabricksAppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_spec(
        self,
    ) -> typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#job_spec DataDatabricksAppsSettingsCustomTemplate#job_spec}.'''
        result = self._values.get("job_spec")
        return typing.cast(typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec"], result)

    @builtins.property
    def secret_spec(
        self,
    ) -> typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#secret_spec DataDatabricksAppsSettingsCustomTemplate#secret_spec}.'''
        result = self._values.get("secret_spec")
        return typing.cast(typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"], result)

    @builtins.property
    def serving_endpoint_spec(
        self,
    ) -> typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#serving_endpoint_spec DataDatabricksAppsSettingsCustomTemplate#serving_endpoint_spec}.'''
        result = self._values.get("serving_endpoint_spec")
        return typing.cast(typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"], result)

    @builtins.property
    def sql_warehouse_spec(
        self,
    ) -> typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#sql_warehouse_spec DataDatabricksAppsSettingsCustomTemplate#sql_warehouse_spec}.'''
        result = self._values.get("sql_warehouse_spec")
        return typing.cast(typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"], result)

    @builtins.property
    def uc_securable_spec(
        self,
    ) -> typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#uc_securable_spec DataDatabricksAppsSettingsCustomTemplate#uc_securable_spec}.'''
        result = self._values.get("uc_securable_spec")
        return typing.cast(typing.Optional["DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9068bef9ebef32c13494f110251976b205f237183c80974863d693b051d20862)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc841129d54c816a260d475f96955248a2623fe4d651127bc7801d04389701e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__503c4ae7ba963e1dd2fbd1a2e911f9a4997a1ce3409001b0a0b0457a0685cc0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef97e1ec42337e2ddd7a76f59a8adede3a0b9fe04f221c21eddaf4cf4a281f33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__369f5e2d1e625b2201997a4cae9fdcc408c1278bbdf884a37aa11e8c808ab020)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16fb92ec87b0978268cfbdc176d519bb980c8ec9ef7b1bc740fbf2332235172d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6f41c0df21a9290daaa368af05f0d033d8b43dc3d51f2159c050a322c9d035f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e0db5284e510107d816b9816e298157ba6061838e0ed6b4c18d20a891a340e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__00e6ea3b87a6fbb5b066f33b7230dae4710058d6c9f74c15d88f041b9bd2bc7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe45ff73df152b7a94c0886939a7733dc4104b6ed4ced875e5fff618e55baac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9f2186f5db12cad25b5e685ae89b34bf6ae6394ee28dcb562249e92f4328e4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putJobSpec")
    def put_job_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putJobSpec", [value]))

    @jsii.member(jsii_name="putSecretSpec")
    def put_secret_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putSecretSpec", [value]))

    @jsii.member(jsii_name="putServingEndpointSpec")
    def put_serving_endpoint_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putServingEndpointSpec", [value]))

    @jsii.member(jsii_name="putSqlWarehouseSpec")
    def put_sql_warehouse_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putSqlWarehouseSpec", [value]))

    @jsii.member(jsii_name="putUcSecurableSpec")
    def put_uc_securable_spec(
        self,
        *,
        permission: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#securable_type DataDatabricksAppsSettingsCustomTemplate#securable_type}.
        '''
        value = DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(
            permission=permission, securable_type=securable_type
        )

        return typing.cast(None, jsii.invoke(self, "putUcSecurableSpec", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetJobSpec")
    def reset_job_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobSpec", []))

    @jsii.member(jsii_name="resetSecretSpec")
    def reset_secret_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretSpec", []))

    @jsii.member(jsii_name="resetServingEndpointSpec")
    def reset_serving_endpoint_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServingEndpointSpec", []))

    @jsii.member(jsii_name="resetSqlWarehouseSpec")
    def reset_sql_warehouse_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlWarehouseSpec", []))

    @jsii.member(jsii_name="resetUcSecurableSpec")
    def reset_uc_securable_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUcSecurableSpec", []))

    @builtins.property
    @jsii.member(jsii_name="jobSpec")
    def job_spec(
        self,
    ) -> DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference:
        return typing.cast(DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference, jsii.get(self, "jobSpec"))

    @builtins.property
    @jsii.member(jsii_name="secretSpec")
    def secret_spec(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference", jsii.get(self, "secretSpec"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointSpec")
    def serving_endpoint_spec(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference", jsii.get(self, "servingEndpointSpec"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseSpec")
    def sql_warehouse_spec(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference", jsii.get(self, "sqlWarehouseSpec"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableSpec")
    def uc_securable_spec(
        self,
    ) -> "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference":
        return typing.cast("DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference", jsii.get(self, "ucSecurableSpec"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="jobSpecInput")
    def job_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]], jsii.get(self, "jobSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretSpecInput")
    def secret_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]], jsii.get(self, "secretSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointSpecInput")
    def serving_endpoint_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]], jsii.get(self, "servingEndpointSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseSpecInput")
    def sql_warehouse_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]], jsii.get(self, "sqlWarehouseSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableSpecInput")
    def uc_securable_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]], jsii.get(self, "ucSecurableSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7a912a7099b63ca43ad01e5285fec185896a8c71557174ca2dec0439a197e3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100532c728c070c7eb3edb4bcf3039ea5834c8d9ef469b285189cccd26511906)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad4c81cc6906e3c1543985498ff802d175b18e863b203edb5f0315ee6d76f4e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b780e9567e62a012b054c9434239c38c88176d1624a4df923b36369d2190fbf6)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f9564644f564b066849364417d4cd2e5f53793103028792ce1ccb8216c3bfb3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a49ee342267753d91280c64b6fc731445953d2f52e6b66e25da540e9818a4e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb48750d6a244215cf6711bbbd91ba538055b892698cad8004e6fddb7c2a0a27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__829c95efc4b7dc6aac100ffb70286be2e44b4361184610b11a45554fd1035207)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__021b593c3a0e67aac5f30cbe656b742f48265f0e6795882fbf62e38ecbcc6b69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46d0f59e318feeb9593c68761798a1fe1a3ebb892207edcf01c5074a4b02a4c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aeaaaee1e1132bc80ba76ea05c69a137e6d4605cb13c1f2614cc0a2aa4d802d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a9471fc51e32d0fbaf0529e346c792140b652a0cb2ac7989132a17f31776948)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c520eac58d6b1059fc09cb714a9c1a9ec74e5fb8a920ebc189df4ac3ef648fd8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae2225701d69ad9113e94c61a7e97b715eebd14b5c40f2b133d5bfb21ce26a06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f08b885479feab578ee67a96d1100ffad531f968e268cd84d86381defe042e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission", "securable_type": "securableType"},
)
class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec:
    def __init__(
        self,
        *,
        permission: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#securable_type DataDatabricksAppsSettingsCustomTemplate#securable_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82db97de6749f633a53bab570c2e131a62a56caa651d13045e6d025317a195f9)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
            check_type(argname="argument securable_type", value=securable_type, expected_type=type_hints["securable_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
            "securable_type": securable_type,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#permission DataDatabricksAppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/data-sources/apps_settings_custom_template#securable_type DataDatabricksAppsSettingsCustomTemplate#securable_type}.'''
        result = self._values.get("securable_type")
        assert result is not None, "Required property 'securable_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksAppsSettingsCustomTemplate.DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a586a3c3d0c6534b51799cde36aed84a0627ddda2ef13d6044f6f65cfe63fd07)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="permissionInput")
    def permission_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionInput"))

    @builtins.property
    @jsii.member(jsii_name="securableTypeInput")
    def securable_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securableTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="permission")
    def permission(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permission"))

    @permission.setter
    def permission(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc6f4ef5d23c3863e1ee0ef4c443a4b403504cb4a9dd8bdcae684a620f7b9c69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableType")
    def securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableType"))

    @securable_type.setter
    def securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ae6588c4654255e16480045c696381c6a7620bb0b05c9f0998cb5c4fbf71f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ccf0c88b240e558d9f71b5c8a4dcf0b49f4cfe412feaf1f5f8905309058d0d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDatabricksAppsSettingsCustomTemplate",
    "DataDatabricksAppsSettingsCustomTemplateConfig",
    "DataDatabricksAppsSettingsCustomTemplateManifest",
    "DataDatabricksAppsSettingsCustomTemplateManifestOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsList",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec",
    "DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference",
]

publication.publish()

def _typecheckingstub__a0d81d142a96da4e3e838a02f14ceee6d4d0cb17c19637f3ece34eb3558f8aa1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    git_provider: builtins.str,
    git_repo: builtins.str,
    manifest: typing.Union[DataDatabricksAppsSettingsCustomTemplateManifest, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    path: builtins.str,
    description: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e9d80a7d70fd5f24b113e4de8acfff9ae24ebc50b6936b65559603409ecf730d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b350a72b857c23731a61f24b3eeb203a8471bf70d539b197bd17f574118f009(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cedeba23c59ba2f00d542f7551e0eb7d22b6fe7f2e8dd9d087123fb4748b7fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e8eae3ca85def3f172ddc432f15f722ebde0a11e5f9280f5f252508c97df42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__179f7056392d6be80199127a25ed5bd02261e2d096a5b2badae03fae0ee36d37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77fe2c516bcf46197751e3fd9e84c4c9595ac8d82a7f315c624ecf338c8c5ecf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf4c02315de4f242bcd106a85fca65d28937f74dbeefa63f08da792ad9037d9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8febf27efd2fdcf1851081eb22c0b5b6a9373bf8e48adcb0e7d57b1c0fc01f68(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    git_provider: builtins.str,
    git_repo: builtins.str,
    manifest: typing.Union[DataDatabricksAppsSettingsCustomTemplateManifest, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    path: builtins.str,
    description: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4842dc41805d24afa739ffb865d04c321187f8ad4e39ee6a8e8a38062dece441(
    *,
    name: builtins.str,
    version: jsii.Number,
    description: typing.Optional[builtins.str] = None,
    resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cddcb925a8527553ec13b9ea7a2afb6fb04ffec820ddb8df6360a93afd97f31(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c00b32dbdd81157a5d90af8cbf387509bd2ba7b112877c02f4d61cfb51f0fe07(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06f69ec949db29dc6aecee8f46cff69c5902fc6adad27fc979f95bae9ba97255(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c39817f447ed72bdbe663d69b87d12803eca2fb4e1363529d7fc4832c4465bb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff06cc627da6a9cb7003741a3406422711c177f80452228d9174dee09cf34918(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed22fe4c87ed255d26b3e22cd9a42ddba1ed4b20e4463a5d842a3ddf4d6fb36(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4952cf4d3ed7e4ef8aea351699e2b41a111aaf2c905ac6092d3c800402bd94f(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    job_spec: typing.Optional[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    secret_spec: typing.Optional[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    serving_endpoint_spec: typing.Optional[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    sql_warehouse_spec: typing.Optional[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    uc_securable_spec: typing.Optional[typing.Union[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9068bef9ebef32c13494f110251976b205f237183c80974863d693b051d20862(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc841129d54c816a260d475f96955248a2623fe4d651127bc7801d04389701e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__503c4ae7ba963e1dd2fbd1a2e911f9a4997a1ce3409001b0a0b0457a0685cc0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef97e1ec42337e2ddd7a76f59a8adede3a0b9fe04f221c21eddaf4cf4a281f33(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsJobSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__369f5e2d1e625b2201997a4cae9fdcc408c1278bbdf884a37aa11e8c808ab020(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16fb92ec87b0978268cfbdc176d519bb980c8ec9ef7b1bc740fbf2332235172d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f41c0df21a9290daaa368af05f0d033d8b43dc3d51f2159c050a322c9d035f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0db5284e510107d816b9816e298157ba6061838e0ed6b4c18d20a891a340e4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e6ea3b87a6fbb5b066f33b7230dae4710058d6c9f74c15d88f041b9bd2bc7d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe45ff73df152b7a94c0886939a7733dc4104b6ed4ced875e5fff618e55baac2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9f2186f5db12cad25b5e685ae89b34bf6ae6394ee28dcb562249e92f4328e4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7a912a7099b63ca43ad01e5285fec185896a8c71557174ca2dec0439a197e3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100532c728c070c7eb3edb4bcf3039ea5834c8d9ef469b285189cccd26511906(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4c81cc6906e3c1543985498ff802d175b18e863b203edb5f0315ee6d76f4e6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b780e9567e62a012b054c9434239c38c88176d1624a4df923b36369d2190fbf6(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f9564644f564b066849364417d4cd2e5f53793103028792ce1ccb8216c3bfb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a49ee342267753d91280c64b6fc731445953d2f52e6b66e25da540e9818a4e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb48750d6a244215cf6711bbbd91ba538055b892698cad8004e6fddb7c2a0a27(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__829c95efc4b7dc6aac100ffb70286be2e44b4361184610b11a45554fd1035207(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__021b593c3a0e67aac5f30cbe656b742f48265f0e6795882fbf62e38ecbcc6b69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d0f59e318feeb9593c68761798a1fe1a3ebb892207edcf01c5074a4b02a4c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aeaaaee1e1132bc80ba76ea05c69a137e6d4605cb13c1f2614cc0a2aa4d802d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9471fc51e32d0fbaf0529e346c792140b652a0cb2ac7989132a17f31776948(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c520eac58d6b1059fc09cb714a9c1a9ec74e5fb8a920ebc189df4ac3ef648fd8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2225701d69ad9113e94c61a7e97b715eebd14b5c40f2b133d5bfb21ce26a06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f08b885479feab578ee67a96d1100ffad531f968e268cd84d86381defe042e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82db97de6749f633a53bab570c2e131a62a56caa651d13045e6d025317a195f9(
    *,
    permission: builtins.str,
    securable_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a586a3c3d0c6534b51799cde36aed84a0627ddda2ef13d6044f6f65cfe63fd07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc6f4ef5d23c3863e1ee0ef4c443a4b403504cb4a9dd8bdcae684a620f7b9c69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ae6588c4654255e16480045c696381c6a7620bb0b05c9f0998cb5c4fbf71f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ccf0c88b240e558d9f71b5c8a4dcf0b49f4cfe412feaf1f5f8905309058d0d7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksAppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]],
) -> None:
    """Type checking stubs"""
    pass
