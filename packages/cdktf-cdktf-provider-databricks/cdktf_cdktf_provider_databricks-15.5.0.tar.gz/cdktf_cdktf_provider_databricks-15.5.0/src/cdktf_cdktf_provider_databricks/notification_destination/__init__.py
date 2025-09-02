r'''
# `databricks_notification_destination`

Refer to the Terraform Registry for docs: [`databricks_notification_destination`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination).
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


class NotificationDestination(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestination",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination databricks_notification_destination}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        display_name: builtins.str,
        config: typing.Optional[typing.Union["NotificationDestinationConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        destination_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination databricks_notification_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#display_name NotificationDestination#display_name}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#config NotificationDestination#config}
        :param destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#destination_type NotificationDestination#destination_type}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#id NotificationDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a18ce5496b8e1799ceb5229a96e78b2bd109aeb01a6763b900e546d023098640)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = NotificationDestinationConfig(
            display_name=display_name,
            config=config,
            destination_type=destination_type,
            id=id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a NotificationDestination resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the NotificationDestination to import.
        :param import_from_id: The id of the existing NotificationDestination that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the NotificationDestination to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6af2aa8d1b88cf55ec7dc066747802785650379df1488527b002e5ae5893467)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        email: typing.Optional[typing.Union["NotificationDestinationConfigEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        generic_webhook: typing.Optional[typing.Union["NotificationDestinationConfigGenericWebhook", typing.Dict[builtins.str, typing.Any]]] = None,
        microsoft_teams: typing.Optional[typing.Union["NotificationDestinationConfigMicrosoftTeams", typing.Dict[builtins.str, typing.Any]]] = None,
        pagerduty: typing.Optional[typing.Union["NotificationDestinationConfigPagerduty", typing.Dict[builtins.str, typing.Any]]] = None,
        slack: typing.Optional[typing.Union["NotificationDestinationConfigSlack", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param email: email block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#email NotificationDestination#email}
        :param generic_webhook: generic_webhook block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#generic_webhook NotificationDestination#generic_webhook}
        :param microsoft_teams: microsoft_teams block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#microsoft_teams NotificationDestination#microsoft_teams}
        :param pagerduty: pagerduty block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#pagerduty NotificationDestination#pagerduty}
        :param slack: slack block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#slack NotificationDestination#slack}
        '''
        value = NotificationDestinationConfigA(
            email=email,
            generic_webhook=generic_webhook,
            microsoft_teams=microsoft_teams,
            pagerduty=pagerduty,
            slack=slack,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetDestinationType")
    def reset_destination_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationType", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "NotificationDestinationConfigAOutputReference":
        return typing.cast("NotificationDestinationConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["NotificationDestinationConfigA"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationTypeInput")
    def destination_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationType")
    def destination_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationType"))

    @destination_type.setter
    def destination_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bed8daab156c1fb8e82f03c314a9dfbb7200b9c2a8098d8d1861ed2357fcca46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d4d2031c1d73a857faa5d4ae73e904ddba9aad85c43aa6513b90bab36cfc57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26d9931241ff804f94152335269153a5eec90cd3fd591b502fbf69ff9de78c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "display_name": "displayName",
        "config": "config",
        "destination_type": "destinationType",
        "id": "id",
    },
)
class NotificationDestinationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        display_name: builtins.str,
        config: typing.Optional[typing.Union["NotificationDestinationConfigA", typing.Dict[builtins.str, typing.Any]]] = None,
        destination_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#display_name NotificationDestination#display_name}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#config NotificationDestination#config}
        :param destination_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#destination_type NotificationDestination#destination_type}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#id NotificationDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = NotificationDestinationConfigA(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031d9307f2952e1f450a488b0be3eb1c6b73fc55f14a5fefa5543a3811c41e13)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument destination_type", value=destination_type, expected_type=type_hints["destination_type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "display_name": display_name,
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
        if config is not None:
            self._values["config"] = config
        if destination_type is not None:
            self._values["destination_type"] = destination_type
        if id is not None:
            self._values["id"] = id

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
    def display_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#display_name NotificationDestination#display_name}.'''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional["NotificationDestinationConfigA"]:
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#config NotificationDestination#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional["NotificationDestinationConfigA"], result)

    @builtins.property
    def destination_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#destination_type NotificationDestination#destination_type}.'''
        result = self._values.get("destination_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#id NotificationDestination#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "generic_webhook": "genericWebhook",
        "microsoft_teams": "microsoftTeams",
        "pagerduty": "pagerduty",
        "slack": "slack",
    },
)
class NotificationDestinationConfigA:
    def __init__(
        self,
        *,
        email: typing.Optional[typing.Union["NotificationDestinationConfigEmail", typing.Dict[builtins.str, typing.Any]]] = None,
        generic_webhook: typing.Optional[typing.Union["NotificationDestinationConfigGenericWebhook", typing.Dict[builtins.str, typing.Any]]] = None,
        microsoft_teams: typing.Optional[typing.Union["NotificationDestinationConfigMicrosoftTeams", typing.Dict[builtins.str, typing.Any]]] = None,
        pagerduty: typing.Optional[typing.Union["NotificationDestinationConfigPagerduty", typing.Dict[builtins.str, typing.Any]]] = None,
        slack: typing.Optional[typing.Union["NotificationDestinationConfigSlack", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param email: email block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#email NotificationDestination#email}
        :param generic_webhook: generic_webhook block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#generic_webhook NotificationDestination#generic_webhook}
        :param microsoft_teams: microsoft_teams block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#microsoft_teams NotificationDestination#microsoft_teams}
        :param pagerduty: pagerduty block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#pagerduty NotificationDestination#pagerduty}
        :param slack: slack block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#slack NotificationDestination#slack}
        '''
        if isinstance(email, dict):
            email = NotificationDestinationConfigEmail(**email)
        if isinstance(generic_webhook, dict):
            generic_webhook = NotificationDestinationConfigGenericWebhook(**generic_webhook)
        if isinstance(microsoft_teams, dict):
            microsoft_teams = NotificationDestinationConfigMicrosoftTeams(**microsoft_teams)
        if isinstance(pagerduty, dict):
            pagerduty = NotificationDestinationConfigPagerduty(**pagerduty)
        if isinstance(slack, dict):
            slack = NotificationDestinationConfigSlack(**slack)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af992e27bc8a71c75665f7179a6ccbebd75f2dc9385d8a63fe898c3ed0b19a6d)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument generic_webhook", value=generic_webhook, expected_type=type_hints["generic_webhook"])
            check_type(argname="argument microsoft_teams", value=microsoft_teams, expected_type=type_hints["microsoft_teams"])
            check_type(argname="argument pagerduty", value=pagerduty, expected_type=type_hints["pagerduty"])
            check_type(argname="argument slack", value=slack, expected_type=type_hints["slack"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email
        if generic_webhook is not None:
            self._values["generic_webhook"] = generic_webhook
        if microsoft_teams is not None:
            self._values["microsoft_teams"] = microsoft_teams
        if pagerduty is not None:
            self._values["pagerduty"] = pagerduty
        if slack is not None:
            self._values["slack"] = slack

    @builtins.property
    def email(self) -> typing.Optional["NotificationDestinationConfigEmail"]:
        '''email block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#email NotificationDestination#email}
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional["NotificationDestinationConfigEmail"], result)

    @builtins.property
    def generic_webhook(
        self,
    ) -> typing.Optional["NotificationDestinationConfigGenericWebhook"]:
        '''generic_webhook block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#generic_webhook NotificationDestination#generic_webhook}
        '''
        result = self._values.get("generic_webhook")
        return typing.cast(typing.Optional["NotificationDestinationConfigGenericWebhook"], result)

    @builtins.property
    def microsoft_teams(
        self,
    ) -> typing.Optional["NotificationDestinationConfigMicrosoftTeams"]:
        '''microsoft_teams block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#microsoft_teams NotificationDestination#microsoft_teams}
        '''
        result = self._values.get("microsoft_teams")
        return typing.cast(typing.Optional["NotificationDestinationConfigMicrosoftTeams"], result)

    @builtins.property
    def pagerduty(self) -> typing.Optional["NotificationDestinationConfigPagerduty"]:
        '''pagerduty block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#pagerduty NotificationDestination#pagerduty}
        '''
        result = self._values.get("pagerduty")
        return typing.cast(typing.Optional["NotificationDestinationConfigPagerduty"], result)

    @builtins.property
    def slack(self) -> typing.Optional["NotificationDestinationConfigSlack"]:
        '''slack block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#slack NotificationDestination#slack}
        '''
        result = self._values.get("slack")
        return typing.cast(typing.Optional["NotificationDestinationConfigSlack"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3bfd011c5aa8ebec3fbcced674903575cabf5b789a1f51abb33368fc632ecf6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putEmail")
    def put_email(
        self,
        *,
        addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#addresses NotificationDestination#addresses}.
        '''
        value = NotificationDestinationConfigEmail(addresses=addresses)

        return typing.cast(None, jsii.invoke(self, "putEmail", [value]))

    @jsii.member(jsii_name="putGenericWebhook")
    def put_generic_webhook(
        self,
        *,
        password: typing.Optional[builtins.str] = None,
        password_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        username_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password NotificationDestination#password}.
        :param password_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password_set NotificationDestination#password_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username NotificationDestination#username}.
        :param username_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username_set NotificationDestination#username_set}.
        '''
        value = NotificationDestinationConfigGenericWebhook(
            password=password,
            password_set=password_set,
            url=url,
            url_set=url_set,
            username=username,
            username_set=username_set,
        )

        return typing.cast(None, jsii.invoke(self, "putGenericWebhook", [value]))

    @jsii.member(jsii_name="putMicrosoftTeams")
    def put_microsoft_teams(
        self,
        *,
        app_id: typing.Optional[builtins.str] = None,
        app_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_secret: typing.Optional[builtins.str] = None,
        auth_secret_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        channel_url: typing.Optional[builtins.str] = None,
        channel_url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tenant_id: typing.Optional[builtins.str] = None,
        tenant_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id NotificationDestination#app_id}.
        :param app_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id_set NotificationDestination#app_id_set}.
        :param auth_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret NotificationDestination#auth_secret}.
        :param auth_secret_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret_set NotificationDestination#auth_secret_set}.
        :param channel_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url NotificationDestination#channel_url}.
        :param channel_url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url_set NotificationDestination#channel_url_set}.
        :param tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id NotificationDestination#tenant_id}.
        :param tenant_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id_set NotificationDestination#tenant_id_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        '''
        value = NotificationDestinationConfigMicrosoftTeams(
            app_id=app_id,
            app_id_set=app_id_set,
            auth_secret=auth_secret,
            auth_secret_set=auth_secret_set,
            channel_url=channel_url,
            channel_url_set=channel_url_set,
            tenant_id=tenant_id,
            tenant_id_set=tenant_id_set,
            url=url,
            url_set=url_set,
        )

        return typing.cast(None, jsii.invoke(self, "putMicrosoftTeams", [value]))

    @jsii.member(jsii_name="putPagerduty")
    def put_pagerduty(
        self,
        *,
        integration_key: typing.Optional[builtins.str] = None,
        integration_key_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param integration_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key NotificationDestination#integration_key}.
        :param integration_key_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key_set NotificationDestination#integration_key_set}.
        '''
        value = NotificationDestinationConfigPagerduty(
            integration_key=integration_key, integration_key_set=integration_key_set
        )

        return typing.cast(None, jsii.invoke(self, "putPagerduty", [value]))

    @jsii.member(jsii_name="putSlack")
    def put_slack(
        self,
        *,
        channel_id: typing.Optional[builtins.str] = None,
        channel_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        oauth_token_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param channel_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id NotificationDestination#channel_id}.
        :param channel_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id_set NotificationDestination#channel_id_set}.
        :param oauth_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token NotificationDestination#oauth_token}.
        :param oauth_token_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token_set NotificationDestination#oauth_token_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        '''
        value = NotificationDestinationConfigSlack(
            channel_id=channel_id,
            channel_id_set=channel_id_set,
            oauth_token=oauth_token,
            oauth_token_set=oauth_token_set,
            url=url,
            url_set=url_set,
        )

        return typing.cast(None, jsii.invoke(self, "putSlack", [value]))

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @jsii.member(jsii_name="resetGenericWebhook")
    def reset_generic_webhook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenericWebhook", []))

    @jsii.member(jsii_name="resetMicrosoftTeams")
    def reset_microsoft_teams(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftTeams", []))

    @jsii.member(jsii_name="resetPagerduty")
    def reset_pagerduty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPagerduty", []))

    @jsii.member(jsii_name="resetSlack")
    def reset_slack(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlack", []))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> "NotificationDestinationConfigEmailOutputReference":
        return typing.cast("NotificationDestinationConfigEmailOutputReference", jsii.get(self, "email"))

    @builtins.property
    @jsii.member(jsii_name="genericWebhook")
    def generic_webhook(
        self,
    ) -> "NotificationDestinationConfigGenericWebhookOutputReference":
        return typing.cast("NotificationDestinationConfigGenericWebhookOutputReference", jsii.get(self, "genericWebhook"))

    @builtins.property
    @jsii.member(jsii_name="microsoftTeams")
    def microsoft_teams(
        self,
    ) -> "NotificationDestinationConfigMicrosoftTeamsOutputReference":
        return typing.cast("NotificationDestinationConfigMicrosoftTeamsOutputReference", jsii.get(self, "microsoftTeams"))

    @builtins.property
    @jsii.member(jsii_name="pagerduty")
    def pagerduty(self) -> "NotificationDestinationConfigPagerdutyOutputReference":
        return typing.cast("NotificationDestinationConfigPagerdutyOutputReference", jsii.get(self, "pagerduty"))

    @builtins.property
    @jsii.member(jsii_name="slack")
    def slack(self) -> "NotificationDestinationConfigSlackOutputReference":
        return typing.cast("NotificationDestinationConfigSlackOutputReference", jsii.get(self, "slack"))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional["NotificationDestinationConfigEmail"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigEmail"], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="genericWebhookInput")
    def generic_webhook_input(
        self,
    ) -> typing.Optional["NotificationDestinationConfigGenericWebhook"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigGenericWebhook"], jsii.get(self, "genericWebhookInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftTeamsInput")
    def microsoft_teams_input(
        self,
    ) -> typing.Optional["NotificationDestinationConfigMicrosoftTeams"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigMicrosoftTeams"], jsii.get(self, "microsoftTeamsInput"))

    @builtins.property
    @jsii.member(jsii_name="pagerdutyInput")
    def pagerduty_input(
        self,
    ) -> typing.Optional["NotificationDestinationConfigPagerduty"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigPagerduty"], jsii.get(self, "pagerdutyInput"))

    @builtins.property
    @jsii.member(jsii_name="slackInput")
    def slack_input(self) -> typing.Optional["NotificationDestinationConfigSlack"]:
        return typing.cast(typing.Optional["NotificationDestinationConfigSlack"], jsii.get(self, "slackInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NotificationDestinationConfigA]:
        return typing.cast(typing.Optional[NotificationDestinationConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigA],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5b42521afd53506c7e437ec9f6dbd71f51bf4903fc7aedfaa8cc3616ccd3574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigEmail",
    jsii_struct_bases=[],
    name_mapping={"addresses": "addresses"},
)
class NotificationDestinationConfigEmail:
    def __init__(
        self,
        *,
        addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#addresses NotificationDestination#addresses}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60baf2d6acc9d7314e1e286b336eedd67f774580c19152e78fa2a0df1e718b82)
            check_type(argname="argument addresses", value=addresses, expected_type=type_hints["addresses"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if addresses is not None:
            self._values["addresses"] = addresses

    @builtins.property
    def addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#addresses NotificationDestination#addresses}.'''
        result = self._values.get("addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigEmail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigEmailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigEmailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd4dc045950861d3d5e11d90a3fd69135c4c81c22182404eb131cfc17e59bd40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAddresses")
    def reset_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddresses", []))

    @builtins.property
    @jsii.member(jsii_name="addressesInput")
    def addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressesInput"))

    @builtins.property
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addresses"))

    @addresses.setter
    def addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e5e04aa00c646b38e5ae38e3c45a8b8fe15623b8fe0af19a05d95e75201cd44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NotificationDestinationConfigEmail]:
        return typing.cast(typing.Optional[NotificationDestinationConfigEmail], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigEmail],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b39997f0d43f191c18904a2e29e053359095a7c97e7906f3edfe47986b3a22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigGenericWebhook",
    jsii_struct_bases=[],
    name_mapping={
        "password": "password",
        "password_set": "passwordSet",
        "url": "url",
        "url_set": "urlSet",
        "username": "username",
        "username_set": "usernameSet",
    },
)
class NotificationDestinationConfigGenericWebhook:
    def __init__(
        self,
        *,
        password: typing.Optional[builtins.str] = None,
        password_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        username_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password NotificationDestination#password}.
        :param password_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password_set NotificationDestination#password_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username NotificationDestination#username}.
        :param username_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username_set NotificationDestination#username_set}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca41a66ec289c58769e74cb2eb27358b094e57aff1b6fd9cf4630070a33e4841)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_set", value=password_set, expected_type=type_hints["password_set"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument url_set", value=url_set, expected_type=type_hints["url_set"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_set", value=username_set, expected_type=type_hints["username_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if password is not None:
            self._values["password"] = password
        if password_set is not None:
            self._values["password_set"] = password_set
        if url is not None:
            self._values["url"] = url
        if url_set is not None:
            self._values["url_set"] = url_set
        if username is not None:
            self._values["username"] = username
        if username_set is not None:
            self._values["username_set"] = username_set

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password NotificationDestination#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#password_set NotificationDestination#password_set}.'''
        result = self._values.get("password_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.'''
        result = self._values.get("url_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username NotificationDestination#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#username_set NotificationDestination#username_set}.'''
        result = self._values.get("username_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigGenericWebhook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigGenericWebhookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigGenericWebhookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2993fc8469649a3bcd7aab5ae7c54bb5bd2211e0cd336feae969c58eb379b72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordSet")
    def reset_password_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordSet", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUrlSet")
    def reset_url_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlSet", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameSet")
    def reset_username_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameSet", []))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordSetInput")
    def password_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "passwordSetInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="urlSetInput")
    def url_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "urlSetInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameSetInput")
    def username_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usernameSetInput"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb0df6280f488172759a90727ecfd08b3250c079a76dd40efe8fa8e7d8d2c01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordSet")
    def password_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "passwordSet"))

    @password_set.setter
    def password_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__157b16219bb7bc2238f4f6a95b2cd7b17112d25319866380c258050ff81e6e3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b08e590cdbe7094fa7d8a4c672615782431a52df3df362c7fa5bf39f6bce19d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlSet")
    def url_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "urlSet"))

    @url_set.setter
    def url_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab8512df64d220f22d09d599fa65ca4ec7eba8b9fd9a01fbd350f151980da1a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00306be1c6e246fa45c4fcac808a8144a26602f690f4b1e6967f9b34b1a8bb08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameSet")
    def username_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usernameSet"))

    @username_set.setter
    def username_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a1c9f9ed61e7eca2ded02707dfbcc82dc023ee7f78fbd13d5c2bfd6df6a7e10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NotificationDestinationConfigGenericWebhook]:
        return typing.cast(typing.Optional[NotificationDestinationConfigGenericWebhook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigGenericWebhook],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b58fbd2386d0c50d000d0d6527a9ef6311ddadc6fac9f335f12f62c115efa081)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigMicrosoftTeams",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "app_id_set": "appIdSet",
        "auth_secret": "authSecret",
        "auth_secret_set": "authSecretSet",
        "channel_url": "channelUrl",
        "channel_url_set": "channelUrlSet",
        "tenant_id": "tenantId",
        "tenant_id_set": "tenantIdSet",
        "url": "url",
        "url_set": "urlSet",
    },
)
class NotificationDestinationConfigMicrosoftTeams:
    def __init__(
        self,
        *,
        app_id: typing.Optional[builtins.str] = None,
        app_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auth_secret: typing.Optional[builtins.str] = None,
        auth_secret_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        channel_url: typing.Optional[builtins.str] = None,
        channel_url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tenant_id: typing.Optional[builtins.str] = None,
        tenant_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id NotificationDestination#app_id}.
        :param app_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id_set NotificationDestination#app_id_set}.
        :param auth_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret NotificationDestination#auth_secret}.
        :param auth_secret_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret_set NotificationDestination#auth_secret_set}.
        :param channel_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url NotificationDestination#channel_url}.
        :param channel_url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url_set NotificationDestination#channel_url_set}.
        :param tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id NotificationDestination#tenant_id}.
        :param tenant_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id_set NotificationDestination#tenant_id_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6939c6bb2a9b1768c0e56632c40d1294edaa48add88e6ca13d42d9b445b370c)
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument app_id_set", value=app_id_set, expected_type=type_hints["app_id_set"])
            check_type(argname="argument auth_secret", value=auth_secret, expected_type=type_hints["auth_secret"])
            check_type(argname="argument auth_secret_set", value=auth_secret_set, expected_type=type_hints["auth_secret_set"])
            check_type(argname="argument channel_url", value=channel_url, expected_type=type_hints["channel_url"])
            check_type(argname="argument channel_url_set", value=channel_url_set, expected_type=type_hints["channel_url_set"])
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
            check_type(argname="argument tenant_id_set", value=tenant_id_set, expected_type=type_hints["tenant_id_set"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument url_set", value=url_set, expected_type=type_hints["url_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if app_id is not None:
            self._values["app_id"] = app_id
        if app_id_set is not None:
            self._values["app_id_set"] = app_id_set
        if auth_secret is not None:
            self._values["auth_secret"] = auth_secret
        if auth_secret_set is not None:
            self._values["auth_secret_set"] = auth_secret_set
        if channel_url is not None:
            self._values["channel_url"] = channel_url
        if channel_url_set is not None:
            self._values["channel_url_set"] = channel_url_set
        if tenant_id is not None:
            self._values["tenant_id"] = tenant_id
        if tenant_id_set is not None:
            self._values["tenant_id_set"] = tenant_id_set
        if url is not None:
            self._values["url"] = url
        if url_set is not None:
            self._values["url_set"] = url_set

    @builtins.property
    def app_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id NotificationDestination#app_id}.'''
        result = self._values.get("app_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_id_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#app_id_set NotificationDestination#app_id_set}.'''
        result = self._values.get("app_id_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auth_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret NotificationDestination#auth_secret}.'''
        result = self._values.get("auth_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_secret_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#auth_secret_set NotificationDestination#auth_secret_set}.'''
        result = self._values.get("auth_secret_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def channel_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url NotificationDestination#channel_url}.'''
        result = self._values.get("channel_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel_url_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_url_set NotificationDestination#channel_url_set}.'''
        result = self._values.get("channel_url_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tenant_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id NotificationDestination#tenant_id}.'''
        result = self._values.get("tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tenant_id_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#tenant_id_set NotificationDestination#tenant_id_set}.'''
        result = self._values.get("tenant_id_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.'''
        result = self._values.get("url_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigMicrosoftTeams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigMicrosoftTeamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigMicrosoftTeamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55d067d63e9475358efa80dcf8338b1bff3b0fdb60327a53ea81ebdfae1e93e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAppId")
    def reset_app_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppId", []))

    @jsii.member(jsii_name="resetAppIdSet")
    def reset_app_id_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppIdSet", []))

    @jsii.member(jsii_name="resetAuthSecret")
    def reset_auth_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthSecret", []))

    @jsii.member(jsii_name="resetAuthSecretSet")
    def reset_auth_secret_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthSecretSet", []))

    @jsii.member(jsii_name="resetChannelUrl")
    def reset_channel_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelUrl", []))

    @jsii.member(jsii_name="resetChannelUrlSet")
    def reset_channel_url_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelUrlSet", []))

    @jsii.member(jsii_name="resetTenantId")
    def reset_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTenantId", []))

    @jsii.member(jsii_name="resetTenantIdSet")
    def reset_tenant_id_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTenantIdSet", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUrlSet")
    def reset_url_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlSet", []))

    @builtins.property
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property
    @jsii.member(jsii_name="appIdSetInput")
    def app_id_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "appIdSetInput"))

    @builtins.property
    @jsii.member(jsii_name="authSecretInput")
    def auth_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="authSecretSetInput")
    def auth_secret_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "authSecretSetInput"))

    @builtins.property
    @jsii.member(jsii_name="channelUrlInput")
    def channel_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="channelUrlSetInput")
    def channel_url_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "channelUrlSetInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantIdInput")
    def tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantIdSetInput")
    def tenant_id_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tenantIdSetInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="urlSetInput")
    def url_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "urlSetInput"))

    @builtins.property
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdb7d7efcb5690587971ec90b0a4c2140a0fa37683fb7a7b86cd537b679640ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="appIdSet")
    def app_id_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "appIdSet"))

    @app_id_set.setter
    def app_id_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0806913ff821e8c1a40c0837091569adbf58530f8fce5d8d77cee747cc106cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appIdSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authSecret")
    def auth_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authSecret"))

    @auth_secret.setter
    def auth_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29d865206ea77469873dd46dceae67df62275551b73526a315f1b9da23791d50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authSecretSet")
    def auth_secret_set(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "authSecretSet"))

    @auth_secret_set.setter
    def auth_secret_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e332dc131fac54f49b9ad75cb514f5c4ee38dba5f50521b977b53e8dfd06d0a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authSecretSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="channelUrl")
    def channel_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelUrl"))

    @channel_url.setter
    def channel_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3932faaed75a425d275992a6fd02d11e97b82bc14c10d1305e84bab494023280)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="channelUrlSet")
    def channel_url_set(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "channelUrlSet"))

    @channel_url_set.setter
    def channel_url_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2019ecdc969d80401536b27f367c49d2f3b7a1958711c1873486c82e36925aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelUrlSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tenantId")
    def tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantId"))

    @tenant_id.setter
    def tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8081dd398c1aad92b7e6b55eca693dfb00fde351b5a47cfe1234f5fe86de29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tenantIdSet")
    def tenant_id_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tenantIdSet"))

    @tenant_id_set.setter
    def tenant_id_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6287906fec2eefd08881bc07d70038d74b477aebf9eb8d54730e15a6e41bb08d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantIdSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc1e3305d899b0ebfe5f7bd372dbbee3e95d8011232093264f83c92f22084fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlSet")
    def url_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "urlSet"))

    @url_set.setter
    def url_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95df027a893de093a5584c4a87319332cb62bf85c4532086f722bb1233eb11ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[NotificationDestinationConfigMicrosoftTeams]:
        return typing.cast(typing.Optional[NotificationDestinationConfigMicrosoftTeams], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigMicrosoftTeams],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c5ad2db40ac6dff6114373d41aecd32fe26d8a7f9e6bb1b151f503edf0f358f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigPagerduty",
    jsii_struct_bases=[],
    name_mapping={
        "integration_key": "integrationKey",
        "integration_key_set": "integrationKeySet",
    },
)
class NotificationDestinationConfigPagerduty:
    def __init__(
        self,
        *,
        integration_key: typing.Optional[builtins.str] = None,
        integration_key_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param integration_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key NotificationDestination#integration_key}.
        :param integration_key_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key_set NotificationDestination#integration_key_set}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95886fd813e44458bb289eb7a295e73587cf257d992dff185bff5b82b704974a)
            check_type(argname="argument integration_key", value=integration_key, expected_type=type_hints["integration_key"])
            check_type(argname="argument integration_key_set", value=integration_key_set, expected_type=type_hints["integration_key_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if integration_key is not None:
            self._values["integration_key"] = integration_key
        if integration_key_set is not None:
            self._values["integration_key_set"] = integration_key_set

    @builtins.property
    def integration_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key NotificationDestination#integration_key}.'''
        result = self._values.get("integration_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_key_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#integration_key_set NotificationDestination#integration_key_set}.'''
        result = self._values.get("integration_key_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigPagerduty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigPagerdutyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigPagerdutyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b198033c0dec09c41ef80091323360e6278f4011c8c329ca9237876eac2341fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIntegrationKey")
    def reset_integration_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationKey", []))

    @jsii.member(jsii_name="resetIntegrationKeySet")
    def reset_integration_key_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationKeySet", []))

    @builtins.property
    @jsii.member(jsii_name="integrationKeyInput")
    def integration_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationKeySetInput")
    def integration_key_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "integrationKeySetInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationKey")
    def integration_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationKey"))

    @integration_key.setter
    def integration_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aefa48ae11498642789efa46ba59e609f23513f252031d3dcf1c39180ba8c1ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="integrationKeySet")
    def integration_key_set(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "integrationKeySet"))

    @integration_key_set.setter
    def integration_key_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f061d816722b08b7d20afbf1df4bc2c83a8bba9e25aba9ff119f860793c67398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationKeySet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NotificationDestinationConfigPagerduty]:
        return typing.cast(typing.Optional[NotificationDestinationConfigPagerduty], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigPagerduty],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43fdf0d024fd2d93b3f85f94f917b468aed1bc62b3972980b8dbefda34cabceb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigSlack",
    jsii_struct_bases=[],
    name_mapping={
        "channel_id": "channelId",
        "channel_id_set": "channelIdSet",
        "oauth_token": "oauthToken",
        "oauth_token_set": "oauthTokenSet",
        "url": "url",
        "url_set": "urlSet",
    },
)
class NotificationDestinationConfigSlack:
    def __init__(
        self,
        *,
        channel_id: typing.Optional[builtins.str] = None,
        channel_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oauth_token: typing.Optional[builtins.str] = None,
        oauth_token_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param channel_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id NotificationDestination#channel_id}.
        :param channel_id_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id_set NotificationDestination#channel_id_set}.
        :param oauth_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token NotificationDestination#oauth_token}.
        :param oauth_token_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token_set NotificationDestination#oauth_token_set}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.
        :param url_set: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__362109240c788a6a95e6759eb61c63cfdb5ed5206ca95ad73694fd86d472dcc9)
            check_type(argname="argument channel_id", value=channel_id, expected_type=type_hints["channel_id"])
            check_type(argname="argument channel_id_set", value=channel_id_set, expected_type=type_hints["channel_id_set"])
            check_type(argname="argument oauth_token", value=oauth_token, expected_type=type_hints["oauth_token"])
            check_type(argname="argument oauth_token_set", value=oauth_token_set, expected_type=type_hints["oauth_token_set"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument url_set", value=url_set, expected_type=type_hints["url_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if channel_id is not None:
            self._values["channel_id"] = channel_id
        if channel_id_set is not None:
            self._values["channel_id_set"] = channel_id_set
        if oauth_token is not None:
            self._values["oauth_token"] = oauth_token
        if oauth_token_set is not None:
            self._values["oauth_token_set"] = oauth_token_set
        if url is not None:
            self._values["url"] = url
        if url_set is not None:
            self._values["url_set"] = url_set

    @builtins.property
    def channel_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id NotificationDestination#channel_id}.'''
        result = self._values.get("channel_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel_id_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#channel_id_set NotificationDestination#channel_id_set}.'''
        result = self._values.get("channel_id_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oauth_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token NotificationDestination#oauth_token}.'''
        result = self._values.get("oauth_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_token_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#oauth_token_set NotificationDestination#oauth_token_set}.'''
        result = self._values.get("oauth_token_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url NotificationDestination#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url_set(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/notification_destination#url_set NotificationDestination#url_set}.'''
        result = self._values.get("url_set")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationDestinationConfigSlack(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NotificationDestinationConfigSlackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.notificationDestination.NotificationDestinationConfigSlackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f6f1825a9a774c4bbf6980e2acad9325407afc455fe9a16793a93ce1d646406)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetChannelId")
    def reset_channel_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelId", []))

    @jsii.member(jsii_name="resetChannelIdSet")
    def reset_channel_id_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelIdSet", []))

    @jsii.member(jsii_name="resetOauthToken")
    def reset_oauth_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthToken", []))

    @jsii.member(jsii_name="resetOauthTokenSet")
    def reset_oauth_token_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOauthTokenSet", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUrlSet")
    def reset_url_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlSet", []))

    @builtins.property
    @jsii.member(jsii_name="channelIdInput")
    def channel_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelIdInput"))

    @builtins.property
    @jsii.member(jsii_name="channelIdSetInput")
    def channel_id_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "channelIdSetInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthTokenInput")
    def oauth_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oauthTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="oauthTokenSetInput")
    def oauth_token_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "oauthTokenSetInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="urlSetInput")
    def url_set_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "urlSetInput"))

    @builtins.property
    @jsii.member(jsii_name="channelId")
    def channel_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelId"))

    @channel_id.setter
    def channel_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7da5f98a9420bcb29454f9bab3ab8303a80ad3bbc31ed25c21b27f1b0090fddd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="channelIdSet")
    def channel_id_set(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "channelIdSet"))

    @channel_id_set.setter
    def channel_id_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d38a6ab108eab247ae5954c25128a5b267b3409d606dd90c9a72cff18576edf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelIdSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oauthToken")
    def oauth_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oauthToken"))

    @oauth_token.setter
    def oauth_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e208e1c4778e57310e41f39f30c86aed8af2a4d735ea7a91e696025a33cc70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oauthToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oauthTokenSet")
    def oauth_token_set(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "oauthTokenSet"))

    @oauth_token_set.setter
    def oauth_token_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fc1e19027a5647b8287fb23eb8dfa6486be43824c003087e7f7cc351c7befe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oauthTokenSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2101f3750ecffe5c9f4f7e72d06c1144b3ad0ece8754db232a6ba0eeb7ea90d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlSet")
    def url_set(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "urlSet"))

    @url_set.setter
    def url_set(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c27565fa9930bc4c8eadc1556cf5f7ccd20ed1e3763daab1bce12570e356a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NotificationDestinationConfigSlack]:
        return typing.cast(typing.Optional[NotificationDestinationConfigSlack], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[NotificationDestinationConfigSlack],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35fc91c5aac7f8dca11d2f15dc9520d23b63c35a32bba9594244e88840e2bf60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "NotificationDestination",
    "NotificationDestinationConfig",
    "NotificationDestinationConfigA",
    "NotificationDestinationConfigAOutputReference",
    "NotificationDestinationConfigEmail",
    "NotificationDestinationConfigEmailOutputReference",
    "NotificationDestinationConfigGenericWebhook",
    "NotificationDestinationConfigGenericWebhookOutputReference",
    "NotificationDestinationConfigMicrosoftTeams",
    "NotificationDestinationConfigMicrosoftTeamsOutputReference",
    "NotificationDestinationConfigPagerduty",
    "NotificationDestinationConfigPagerdutyOutputReference",
    "NotificationDestinationConfigSlack",
    "NotificationDestinationConfigSlackOutputReference",
]

publication.publish()

def _typecheckingstub__a18ce5496b8e1799ceb5229a96e78b2bd109aeb01a6763b900e546d023098640(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    display_name: builtins.str,
    config: typing.Optional[typing.Union[NotificationDestinationConfigA, typing.Dict[builtins.str, typing.Any]]] = None,
    destination_type: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a6af2aa8d1b88cf55ec7dc066747802785650379df1488527b002e5ae5893467(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bed8daab156c1fb8e82f03c314a9dfbb7200b9c2a8098d8d1861ed2357fcca46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d4d2031c1d73a857faa5d4ae73e904ddba9aad85c43aa6513b90bab36cfc57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26d9931241ff804f94152335269153a5eec90cd3fd591b502fbf69ff9de78c72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__031d9307f2952e1f450a488b0be3eb1c6b73fc55f14a5fefa5543a3811c41e13(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: builtins.str,
    config: typing.Optional[typing.Union[NotificationDestinationConfigA, typing.Dict[builtins.str, typing.Any]]] = None,
    destination_type: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af992e27bc8a71c75665f7179a6ccbebd75f2dc9385d8a63fe898c3ed0b19a6d(
    *,
    email: typing.Optional[typing.Union[NotificationDestinationConfigEmail, typing.Dict[builtins.str, typing.Any]]] = None,
    generic_webhook: typing.Optional[typing.Union[NotificationDestinationConfigGenericWebhook, typing.Dict[builtins.str, typing.Any]]] = None,
    microsoft_teams: typing.Optional[typing.Union[NotificationDestinationConfigMicrosoftTeams, typing.Dict[builtins.str, typing.Any]]] = None,
    pagerduty: typing.Optional[typing.Union[NotificationDestinationConfigPagerduty, typing.Dict[builtins.str, typing.Any]]] = None,
    slack: typing.Optional[typing.Union[NotificationDestinationConfigSlack, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3bfd011c5aa8ebec3fbcced674903575cabf5b789a1f51abb33368fc632ecf6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b42521afd53506c7e437ec9f6dbd71f51bf4903fc7aedfaa8cc3616ccd3574(
    value: typing.Optional[NotificationDestinationConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60baf2d6acc9d7314e1e286b336eedd67f774580c19152e78fa2a0df1e718b82(
    *,
    addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4dc045950861d3d5e11d90a3fd69135c4c81c22182404eb131cfc17e59bd40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5e04aa00c646b38e5ae38e3c45a8b8fe15623b8fe0af19a05d95e75201cd44(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b39997f0d43f191c18904a2e29e053359095a7c97e7906f3edfe47986b3a22(
    value: typing.Optional[NotificationDestinationConfigEmail],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca41a66ec289c58769e74cb2eb27358b094e57aff1b6fd9cf4630070a33e4841(
    *,
    password: typing.Optional[builtins.str] = None,
    password_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
    username_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2993fc8469649a3bcd7aab5ae7c54bb5bd2211e0cd336feae969c58eb379b72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb0df6280f488172759a90727ecfd08b3250c079a76dd40efe8fa8e7d8d2c01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157b16219bb7bc2238f4f6a95b2cd7b17112d25319866380c258050ff81e6e3f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b08e590cdbe7094fa7d8a4c672615782431a52df3df362c7fa5bf39f6bce19d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab8512df64d220f22d09d599fa65ca4ec7eba8b9fd9a01fbd350f151980da1a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00306be1c6e246fa45c4fcac808a8144a26602f690f4b1e6967f9b34b1a8bb08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a1c9f9ed61e7eca2ded02707dfbcc82dc023ee7f78fbd13d5c2bfd6df6a7e10(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b58fbd2386d0c50d000d0d6527a9ef6311ddadc6fac9f335f12f62c115efa081(
    value: typing.Optional[NotificationDestinationConfigGenericWebhook],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6939c6bb2a9b1768c0e56632c40d1294edaa48add88e6ca13d42d9b445b370c(
    *,
    app_id: typing.Optional[builtins.str] = None,
    app_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auth_secret: typing.Optional[builtins.str] = None,
    auth_secret_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    channel_url: typing.Optional[builtins.str] = None,
    channel_url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tenant_id: typing.Optional[builtins.str] = None,
    tenant_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d067d63e9475358efa80dcf8338b1bff3b0fdb60327a53ea81ebdfae1e93e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdb7d7efcb5690587971ec90b0a4c2140a0fa37683fb7a7b86cd537b679640ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0806913ff821e8c1a40c0837091569adbf58530f8fce5d8d77cee747cc106cb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d865206ea77469873dd46dceae67df62275551b73526a315f1b9da23791d50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e332dc131fac54f49b9ad75cb514f5c4ee38dba5f50521b977b53e8dfd06d0a4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3932faaed75a425d275992a6fd02d11e97b82bc14c10d1305e84bab494023280(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2019ecdc969d80401536b27f367c49d2f3b7a1958711c1873486c82e36925aee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8081dd398c1aad92b7e6b55eca693dfb00fde351b5a47cfe1234f5fe86de29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6287906fec2eefd08881bc07d70038d74b477aebf9eb8d54730e15a6e41bb08d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc1e3305d899b0ebfe5f7bd372dbbee3e95d8011232093264f83c92f22084fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95df027a893de093a5584c4a87319332cb62bf85c4532086f722bb1233eb11ef(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c5ad2db40ac6dff6114373d41aecd32fe26d8a7f9e6bb1b151f503edf0f358f(
    value: typing.Optional[NotificationDestinationConfigMicrosoftTeams],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95886fd813e44458bb289eb7a295e73587cf257d992dff185bff5b82b704974a(
    *,
    integration_key: typing.Optional[builtins.str] = None,
    integration_key_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b198033c0dec09c41ef80091323360e6278f4011c8c329ca9237876eac2341fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aefa48ae11498642789efa46ba59e609f23513f252031d3dcf1c39180ba8c1ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f061d816722b08b7d20afbf1df4bc2c83a8bba9e25aba9ff119f860793c67398(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43fdf0d024fd2d93b3f85f94f917b468aed1bc62b3972980b8dbefda34cabceb(
    value: typing.Optional[NotificationDestinationConfigPagerduty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__362109240c788a6a95e6759eb61c63cfdb5ed5206ca95ad73694fd86d472dcc9(
    *,
    channel_id: typing.Optional[builtins.str] = None,
    channel_id_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oauth_token: typing.Optional[builtins.str] = None,
    oauth_token_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    url_set: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f6f1825a9a774c4bbf6980e2acad9325407afc455fe9a16793a93ce1d646406(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7da5f98a9420bcb29454f9bab3ab8303a80ad3bbc31ed25c21b27f1b0090fddd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d38a6ab108eab247ae5954c25128a5b267b3409d606dd90c9a72cff18576edf0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e208e1c4778e57310e41f39f30c86aed8af2a4d735ea7a91e696025a33cc70(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fc1e19027a5647b8287fb23eb8dfa6486be43824c003087e7f7cc351c7befe1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2101f3750ecffe5c9f4f7e72d06c1144b3ad0ece8754db232a6ba0eeb7ea90d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c27565fa9930bc4c8eadc1556cf5f7ccd20ed1e3763daab1bce12570e356a4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35fc91c5aac7f8dca11d2f15dc9520d23b63c35a32bba9594244e88840e2bf60(
    value: typing.Optional[NotificationDestinationConfigSlack],
) -> None:
    """Type checking stubs"""
    pass
