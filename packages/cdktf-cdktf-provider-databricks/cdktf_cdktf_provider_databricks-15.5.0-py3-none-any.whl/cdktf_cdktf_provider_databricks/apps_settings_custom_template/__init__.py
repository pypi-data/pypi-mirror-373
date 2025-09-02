r'''
# `databricks_apps_settings_custom_template`

Refer to the Terraform Registry for docs: [`databricks_apps_settings_custom_template`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template).
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


class AppsSettingsCustomTemplate(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplate",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template databricks_apps_settings_custom_template}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        git_provider: builtins.str,
        git_repo: builtins.str,
        manifest: typing.Union["AppsSettingsCustomTemplateManifest", typing.Dict[builtins.str, typing.Any]],
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
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template databricks_apps_settings_custom_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param git_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_provider AppsSettingsCustomTemplate#git_provider}.
        :param git_repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_repo AppsSettingsCustomTemplate#git_repo}.
        :param manifest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#manifest AppsSettingsCustomTemplate#manifest}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#path AppsSettingsCustomTemplate#path}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#workspace_id AppsSettingsCustomTemplate#workspace_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fc243ea1121d242fe73429f2d76e4312374f464ea1cd41e22680d7c70e29d59)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AppsSettingsCustomTemplateConfig(
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
        '''Generates CDKTF code for importing a AppsSettingsCustomTemplate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AppsSettingsCustomTemplate to import.
        :param import_from_id: The id of the existing AppsSettingsCustomTemplate that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AppsSettingsCustomTemplate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da8a1beacf3d1918c5fad5d3aa2539dd5649a65b38cc467d6564ef29d240f338)
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
        resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#version AppsSettingsCustomTemplate#version}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.
        :param resource_specs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#resource_specs AppsSettingsCustomTemplate#resource_specs}.
        '''
        value = AppsSettingsCustomTemplateManifest(
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
    def manifest(self) -> "AppsSettingsCustomTemplateManifestOutputReference":
        return typing.cast("AppsSettingsCustomTemplateManifestOutputReference", jsii.get(self, "manifest"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifest"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifest"]], jsii.get(self, "manifestInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__6821ced94eee3f28b9c23509e4a0d4d62117e44f7e2e7984b16b7989723c0fc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitProvider")
    def git_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitProvider"))

    @git_provider.setter
    def git_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6674a40f07baa26bc0b4bad2801f68ee2329c4dfc3e94ec69516a846f0e5363a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gitRepo")
    def git_repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitRepo"))

    @git_repo.setter
    def git_repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf9c8f3913bcbcf1cf819ee3fd0ba606ed9fa97192a8afd33d7a1666fdf37b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitRepo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b78026db81405508ed672e2154af2c1bdec211c92bd388d9d17996dfad5f28da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f67cca9851dacc1a547f73b2f54ad5d650d4a8cf1fcf5daf6f79d8283385fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a84ec184c53c63c95fe84f216570759c6b21bf2ef039ea73c63a842a6b21a271)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateConfig",
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
class AppsSettingsCustomTemplateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        manifest: typing.Union["AppsSettingsCustomTemplateManifest", typing.Dict[builtins.str, typing.Any]],
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
        :param git_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_provider AppsSettingsCustomTemplate#git_provider}.
        :param git_repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_repo AppsSettingsCustomTemplate#git_repo}.
        :param manifest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#manifest AppsSettingsCustomTemplate#manifest}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#path AppsSettingsCustomTemplate#path}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#workspace_id AppsSettingsCustomTemplate#workspace_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(manifest, dict):
            manifest = AppsSettingsCustomTemplateManifest(**manifest)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04b84e79732be2d209cf5bb499e3cd94a7a06e32327d96718e5b5c3b5579e50b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_provider AppsSettingsCustomTemplate#git_provider}.'''
        result = self._values.get("git_provider")
        assert result is not None, "Required property 'git_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def git_repo(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#git_repo AppsSettingsCustomTemplate#git_repo}.'''
        result = self._values.get("git_repo")
        assert result is not None, "Required property 'git_repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def manifest(self) -> "AppsSettingsCustomTemplateManifest":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#manifest AppsSettingsCustomTemplate#manifest}.'''
        result = self._values.get("manifest")
        assert result is not None, "Required property 'manifest' is missing"
        return typing.cast("AppsSettingsCustomTemplateManifest", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#path AppsSettingsCustomTemplate#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#workspace_id AppsSettingsCustomTemplate#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifest",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "version": "version",
        "description": "description",
        "resource_specs": "resourceSpecs",
    },
)
class AppsSettingsCustomTemplateManifest:
    def __init__(
        self,
        *,
        name: builtins.str,
        version: jsii.Number,
        description: typing.Optional[builtins.str] = None,
        resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#version AppsSettingsCustomTemplate#version}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.
        :param resource_specs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#resource_specs AppsSettingsCustomTemplate#resource_specs}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7159601a0339ecc986b2ee99579bdffa6d93b1d2a7f0e33bf053458591a6c41a)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#version AppsSettingsCustomTemplate#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_specs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AppsSettingsCustomTemplateManifestResourceSpecs"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#resource_specs AppsSettingsCustomTemplate#resource_specs}.'''
        result = self._values.get("resource_specs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AppsSettingsCustomTemplateManifestResourceSpecs"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad64e3a1e9f5b197b7c27c4b43332a5c25613ec4748e5312132ea2f888eafc69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putResourceSpecs")
    def put_resource_specs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f77a1c8b49e18eab6f70d64ae2113e868efdc842ef9913052fe0ffc2d32f4c)
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
    def resource_specs(self) -> "AppsSettingsCustomTemplateManifestResourceSpecsList":
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsList", jsii.get(self, "resourceSpecs"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AppsSettingsCustomTemplateManifestResourceSpecs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AppsSettingsCustomTemplateManifestResourceSpecs"]]], jsii.get(self, "resourceSpecsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2069251be2812f7c6c7f018c89075b542d630698c4b621bbbc724a3b079449c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5925df5070c2e152adb217d21c60f5c2eb0582f1e88e367bbe1c793631e8361d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @version.setter
    def version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e924671ae91b45abfd741f15b6df444b0d600afc78afe18938cf20c2920481c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifest]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifest]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifest]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab5322cbccfa4ef81a58b2c1dfd002bcbc6e9bce7b988274e4056cbb58225b30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecs",
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
class AppsSettingsCustomTemplateManifestResourceSpecs:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        job_spec: typing.Optional[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecsJobSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        secret_spec: typing.Optional[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        serving_endpoint_spec: typing.Optional[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        sql_warehouse_spec: typing.Optional[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        uc_securable_spec: typing.Optional[typing.Union["AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.
        :param job_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#job_spec AppsSettingsCustomTemplate#job_spec}.
        :param secret_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#secret_spec AppsSettingsCustomTemplate#secret_spec}.
        :param serving_endpoint_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#serving_endpoint_spec AppsSettingsCustomTemplate#serving_endpoint_spec}.
        :param sql_warehouse_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#sql_warehouse_spec AppsSettingsCustomTemplate#sql_warehouse_spec}.
        :param uc_securable_spec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#uc_securable_spec AppsSettingsCustomTemplate#uc_securable_spec}.
        '''
        if isinstance(job_spec, dict):
            job_spec = AppsSettingsCustomTemplateManifestResourceSpecsJobSpec(**job_spec)
        if isinstance(secret_spec, dict):
            secret_spec = AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(**secret_spec)
        if isinstance(serving_endpoint_spec, dict):
            serving_endpoint_spec = AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(**serving_endpoint_spec)
        if isinstance(sql_warehouse_spec, dict):
            sql_warehouse_spec = AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(**sql_warehouse_spec)
        if isinstance(uc_securable_spec, dict):
            uc_securable_spec = AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(**uc_securable_spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64d183dadee6d003b97faed318e06ec6b4349784232b26263f37faa31620232d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#name AppsSettingsCustomTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#description AppsSettingsCustomTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_spec(
        self,
    ) -> typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsJobSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#job_spec AppsSettingsCustomTemplate#job_spec}.'''
        result = self._values.get("job_spec")
        return typing.cast(typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsJobSpec"], result)

    @builtins.property
    def secret_spec(
        self,
    ) -> typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#secret_spec AppsSettingsCustomTemplate#secret_spec}.'''
        result = self._values.get("secret_spec")
        return typing.cast(typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"], result)

    @builtins.property
    def serving_endpoint_spec(
        self,
    ) -> typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#serving_endpoint_spec AppsSettingsCustomTemplate#serving_endpoint_spec}.'''
        result = self._values.get("serving_endpoint_spec")
        return typing.cast(typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"], result)

    @builtins.property
    def sql_warehouse_spec(
        self,
    ) -> typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#sql_warehouse_spec AppsSettingsCustomTemplate#sql_warehouse_spec}.'''
        result = self._values.get("sql_warehouse_spec")
        return typing.cast(typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"], result)

    @builtins.property
    def uc_securable_spec(
        self,
    ) -> typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#uc_securable_spec AppsSettingsCustomTemplate#uc_securable_spec}.'''
        result = self._values.get("uc_securable_spec")
        return typing.cast(typing.Optional["AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsJobSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class AppsSettingsCustomTemplateManifestResourceSpecsJobSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0363aee73d0f8b7e9881375e2495276140d49e9c0ea87d464a6ab67f80976d13)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecsJobSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bbb40dabf4c264d387bfc760b0eb269ef77026853891aa331eb223b65b4358c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__985c6853501ceb51e019f32c16fd9fc9a6102cdd88e6cd89f41e6ecda66d3b1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e74a26156e8adfd26da1312f123d4002baaf6771dcdc760ff44e9a36754f648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AppsSettingsCustomTemplateManifestResourceSpecsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__53dc5d55a76d3b24b9e286eda40b8ae893f9905db0c5dbd06da56869a203ea4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AppsSettingsCustomTemplateManifestResourceSpecsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2578f843b2e505ff240d5a666282f695d0c4dc77b5968525cb8f22b5e35335ba)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ef67e390baae58f1bc07a5e18e0271041163c04cee755c384ebd22f2761f9d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__418c585aa47df4b67bfb46d2118fd54a1a7bcae6cf7839f05e753ede0a657a37)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c2d50905121d4d78977d3826e5d046b72e7244cf4810ea020475833dfff79c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AppsSettingsCustomTemplateManifestResourceSpecs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AppsSettingsCustomTemplateManifestResourceSpecs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AppsSettingsCustomTemplateManifestResourceSpecs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__411c6214dbd874c72da9472c6df7ff01bacdda00ebac354f67090c8b6853e395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AppsSettingsCustomTemplateManifestResourceSpecsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fcca3d9b2491c7d5f326fc3765b5f70729dab82ca298274c3a651a6e76e0835)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putJobSpec")
    def put_job_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        value = AppsSettingsCustomTemplateManifestResourceSpecsJobSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putJobSpec", [value]))

    @jsii.member(jsii_name="putSecretSpec")
    def put_secret_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        value = AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putSecretSpec", [value]))

    @jsii.member(jsii_name="putServingEndpointSpec")
    def put_serving_endpoint_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        value = AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(
            permission=permission
        )

        return typing.cast(None, jsii.invoke(self, "putServingEndpointSpec", [value]))

    @jsii.member(jsii_name="putSqlWarehouseSpec")
    def put_sql_warehouse_spec(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        value = AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(
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
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#securable_type AppsSettingsCustomTemplate#securable_type}.
        '''
        value = AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(
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
    ) -> AppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference:
        return typing.cast(AppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference, jsii.get(self, "jobSpec"))

    @builtins.property
    @jsii.member(jsii_name="secretSpec")
    def secret_spec(
        self,
    ) -> "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference":
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference", jsii.get(self, "secretSpec"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointSpec")
    def serving_endpoint_spec(
        self,
    ) -> "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference":
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference", jsii.get(self, "servingEndpointSpec"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseSpec")
    def sql_warehouse_spec(
        self,
    ) -> "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference":
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference", jsii.get(self, "sqlWarehouseSpec"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableSpec")
    def uc_securable_spec(
        self,
    ) -> "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference":
        return typing.cast("AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference", jsii.get(self, "ucSecurableSpec"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="jobSpecInput")
    def job_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]], jsii.get(self, "jobSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretSpecInput")
    def secret_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec"]], jsii.get(self, "secretSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="servingEndpointSpecInput")
    def serving_endpoint_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec"]], jsii.get(self, "servingEndpointSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlWarehouseSpecInput")
    def sql_warehouse_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec"]], jsii.get(self, "sqlWarehouseSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="ucSecurableSpecInput")
    def uc_securable_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec"]], jsii.get(self, "ucSecurableSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f420ad00059958ad2e6651c11d2f3ebfaccb9f2c5d75563eef70b346d662f9cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd30ea23366d97cc8982ae14010a776acf8ef5ba135a14ba7c0d0f3f6b77c0dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eceeae49f9d9c30b43ad4146b0070511ad77fda9efff7a75b06cb6f8d5d7acbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3a665dc348f6b4eb11fa434afb9c866c990e2db9d8cba369bbd62b929eefa6a)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8038e43128354c5839490afdbf0862629575552fede069a4fe20965d2f2ebe0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__496f56431f21b8d24e2e0a165af0e5037607face1cc146a422aa7f45caa1768b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4afc7a5f47b610d2ec083bc78e4a4aadd9532fd10e8bf175de17ff327861c792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e4c22bfbc9d5bf1ea3c45c048ee562e6a831399124ced304274c3d41f108744)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__305b8d184a385b8c6ef645e7473b8ca4c294414715c624803a5cfdf700b96c52)
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
            type_hints = typing.get_type_hints(_typecheckingstub__76760f3d1046a9dd77ccfd57a6155df761b585bd5161c33af4d57154045ae0e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70627e7934abe0e8ce7ded7b776e4c6005c7ed10f3ad74670dbbe2e3b6f14994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission"},
)
class AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec:
    def __init__(self, *, permission: builtins.str) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__521f272fff570f939bdcbb06f1bbfab58fb008def81f684e3468f794ba596719)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b51bdf6dff7dccdce89599287c1eda2f7ade76947a1cdd0f9c37dbee16156bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5201e169a8b607b929555a376ceff3e8230953ff6938f437906862946ba0b1ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d1fcdda36e245d616c92a500e023fb3d31c889af4a600f729d73d1c205cb6bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec",
    jsii_struct_bases=[],
    name_mapping={"permission": "permission", "securable_type": "securableType"},
)
class AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec:
    def __init__(
        self,
        *,
        permission: builtins.str,
        securable_type: builtins.str,
    ) -> None:
        '''
        :param permission: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.
        :param securable_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#securable_type AppsSettingsCustomTemplate#securable_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c79be5b8b9bd38398aa9893e5f2f30586a91f1448bdb5b2577f820fc0cafb2)
            check_type(argname="argument permission", value=permission, expected_type=type_hints["permission"])
            check_type(argname="argument securable_type", value=securable_type, expected_type=type_hints["securable_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission": permission,
            "securable_type": securable_type,
        }

    @builtins.property
    def permission(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#permission AppsSettingsCustomTemplate#permission}.'''
        result = self._values.get("permission")
        assert result is not None, "Required property 'permission' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def securable_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/apps_settings_custom_template#securable_type AppsSettingsCustomTemplate#securable_type}.'''
        result = self._values.get("securable_type")
        assert result is not None, "Required property 'securable_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.appsSettingsCustomTemplate.AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f4c1804ba5a31b9816335508abde93d8ceedd6d3e3a28b87e0e0585e5fb2a5a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__703e3b63dbbcb5e6d9f663f6c3eae4056029ef6b648f21e6f852aa851c0b7971)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permission", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securableType")
    def securable_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securableType"))

    @securable_type.setter
    def securable_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96216b24cf464d7ba3aa0af90c39e79e346c7a13303ee0252960d1d63561e2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securableType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1743f51570675ba11d4f2113c0f1bfc7fe969e5caa6e37eef23a2122ec7791e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AppsSettingsCustomTemplate",
    "AppsSettingsCustomTemplateConfig",
    "AppsSettingsCustomTemplateManifest",
    "AppsSettingsCustomTemplateManifestOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecs",
    "AppsSettingsCustomTemplateManifestResourceSpecsJobSpec",
    "AppsSettingsCustomTemplateManifestResourceSpecsJobSpecOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecsList",
    "AppsSettingsCustomTemplateManifestResourceSpecsOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec",
    "AppsSettingsCustomTemplateManifestResourceSpecsSecretSpecOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec",
    "AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpecOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec",
    "AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpecOutputReference",
    "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec",
    "AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpecOutputReference",
]

publication.publish()

def _typecheckingstub__5fc243ea1121d242fe73429f2d76e4312374f464ea1cd41e22680d7c70e29d59(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    git_provider: builtins.str,
    git_repo: builtins.str,
    manifest: typing.Union[AppsSettingsCustomTemplateManifest, typing.Dict[builtins.str, typing.Any]],
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

def _typecheckingstub__da8a1beacf3d1918c5fad5d3aa2539dd5649a65b38cc467d6564ef29d240f338(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6821ced94eee3f28b9c23509e4a0d4d62117e44f7e2e7984b16b7989723c0fc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6674a40f07baa26bc0b4bad2801f68ee2329c4dfc3e94ec69516a846f0e5363a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf9c8f3913bcbcf1cf819ee3fd0ba606ed9fa97192a8afd33d7a1666fdf37b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78026db81405508ed672e2154af2c1bdec211c92bd388d9d17996dfad5f28da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f67cca9851dacc1a547f73b2f54ad5d650d4a8cf1fcf5daf6f79d8283385fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a84ec184c53c63c95fe84f216570759c6b21bf2ef039ea73c63a842a6b21a271(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b84e79732be2d209cf5bb499e3cd94a7a06e32327d96718e5b5c3b5579e50b(
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
    manifest: typing.Union[AppsSettingsCustomTemplateManifest, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    path: builtins.str,
    description: typing.Optional[builtins.str] = None,
    workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7159601a0339ecc986b2ee99579bdffa6d93b1d2a7f0e33bf053458591a6c41a(
    *,
    name: builtins.str,
    version: jsii.Number,
    description: typing.Optional[builtins.str] = None,
    resource_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecs, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad64e3a1e9f5b197b7c27c4b43332a5c25613ec4748e5312132ea2f888eafc69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f77a1c8b49e18eab6f70d64ae2113e868efdc842ef9913052fe0ffc2d32f4c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2069251be2812f7c6c7f018c89075b542d630698c4b621bbbc724a3b079449c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5925df5070c2e152adb217d21c60f5c2eb0582f1e88e367bbe1c793631e8361d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e924671ae91b45abfd741f15b6df444b0d600afc78afe18938cf20c2920481c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5322cbccfa4ef81a58b2c1dfd002bcbc6e9bce7b988274e4056cbb58225b30(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64d183dadee6d003b97faed318e06ec6b4349784232b26263f37faa31620232d(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    job_spec: typing.Optional[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecsJobSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    secret_spec: typing.Optional[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    serving_endpoint_spec: typing.Optional[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    sql_warehouse_spec: typing.Optional[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    uc_securable_spec: typing.Optional[typing.Union[AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0363aee73d0f8b7e9881375e2495276140d49e9c0ea87d464a6ab67f80976d13(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bbb40dabf4c264d387bfc760b0eb269ef77026853891aa331eb223b65b4358c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__985c6853501ceb51e019f32c16fd9fc9a6102cdd88e6cd89f41e6ecda66d3b1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e74a26156e8adfd26da1312f123d4002baaf6771dcdc760ff44e9a36754f648(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsJobSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53dc5d55a76d3b24b9e286eda40b8ae893f9905db0c5dbd06da56869a203ea4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2578f843b2e505ff240d5a666282f695d0c4dc77b5968525cb8f22b5e35335ba(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ef67e390baae58f1bc07a5e18e0271041163c04cee755c384ebd22f2761f9d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418c585aa47df4b67bfb46d2118fd54a1a7bcae6cf7839f05e753ede0a657a37(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c2d50905121d4d78977d3826e5d046b72e7244cf4810ea020475833dfff79c2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__411c6214dbd874c72da9472c6df7ff01bacdda00ebac354f67090c8b6853e395(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AppsSettingsCustomTemplateManifestResourceSpecs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fcca3d9b2491c7d5f326fc3765b5f70729dab82ca298274c3a651a6e76e0835(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f420ad00059958ad2e6651c11d2f3ebfaccb9f2c5d75563eef70b346d662f9cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd30ea23366d97cc8982ae14010a776acf8ef5ba135a14ba7c0d0f3f6b77c0dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eceeae49f9d9c30b43ad4146b0070511ad77fda9efff7a75b06cb6f8d5d7acbe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3a665dc348f6b4eb11fa434afb9c866c990e2db9d8cba369bbd62b929eefa6a(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8038e43128354c5839490afdbf0862629575552fede069a4fe20965d2f2ebe0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__496f56431f21b8d24e2e0a165af0e5037607face1cc146a422aa7f45caa1768b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4afc7a5f47b610d2ec083bc78e4a4aadd9532fd10e8bf175de17ff327861c792(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSecretSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e4c22bfbc9d5bf1ea3c45c048ee562e6a831399124ced304274c3d41f108744(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__305b8d184a385b8c6ef645e7473b8ca4c294414715c624803a5cfdf700b96c52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76760f3d1046a9dd77ccfd57a6155df761b585bd5161c33af4d57154045ae0e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70627e7934abe0e8ce7ded7b776e4c6005c7ed10f3ad74670dbbe2e3b6f14994(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsServingEndpointSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__521f272fff570f939bdcbb06f1bbfab58fb008def81f684e3468f794ba596719(
    *,
    permission: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b51bdf6dff7dccdce89599287c1eda2f7ade76947a1cdd0f9c37dbee16156bf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5201e169a8b607b929555a376ceff3e8230953ff6938f437906862946ba0b1ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d1fcdda36e245d616c92a500e023fb3d31c889af4a600f729d73d1c205cb6bc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsSqlWarehouseSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c79be5b8b9bd38398aa9893e5f2f30586a91f1448bdb5b2577f820fc0cafb2(
    *,
    permission: builtins.str,
    securable_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f4c1804ba5a31b9816335508abde93d8ceedd6d3e3a28b87e0e0585e5fb2a5a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703e3b63dbbcb5e6d9f663f6c3eae4056029ef6b648f21e6f852aa851c0b7971(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96216b24cf464d7ba3aa0af90c39e79e346c7a13303ee0252960d1d63561e2a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1743f51570675ba11d4f2113c0f1bfc7fe969e5caa6e37eef23a2122ec7791e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AppsSettingsCustomTemplateManifestResourceSpecsUcSecurableSpec]],
) -> None:
    """Type checking stubs"""
    pass
