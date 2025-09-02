r'''
# `databricks_external_location`

Refer to the Terraform Registry for docs: [`databricks_external_location`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location).
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


class ExternalLocation(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocation",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location databricks_external_location}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        credential_name: builtins.str,
        name: builtins.str,
        url: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_details: typing.Optional[typing.Union["ExternalLocationEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        file_event_queue: typing.Optional[typing.Union["ExternalLocationFileEventQueue", typing.Dict[builtins.str, typing.Any]]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        isolation_mode: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location databricks_external_location} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#credential_name ExternalLocation#credential_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#name ExternalLocation#name}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#url ExternalLocation#url}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#comment ExternalLocation#comment}.
        :param enable_file_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#enable_file_events ExternalLocation#enable_file_events}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#encryption_details ExternalLocation#encryption_details}
        :param fallback: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#fallback ExternalLocation#fallback}.
        :param file_event_queue: file_event_queue block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#file_event_queue ExternalLocation#file_event_queue}
        :param force_destroy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_destroy ExternalLocation#force_destroy}.
        :param force_update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_update ExternalLocation#force_update}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#id ExternalLocation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param isolation_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#isolation_mode ExternalLocation#isolation_mode}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#metastore_id ExternalLocation#metastore_id}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#owner ExternalLocation#owner}.
        :param read_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#read_only ExternalLocation#read_only}.
        :param skip_validation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#skip_validation ExternalLocation#skip_validation}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7366cd3e0f3652d837eb42745a814fa1e20ee0a42261b2fa98aa1a946825cc7e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ExternalLocationConfig(
            credential_name=credential_name,
            name=name,
            url=url,
            comment=comment,
            enable_file_events=enable_file_events,
            encryption_details=encryption_details,
            fallback=fallback,
            file_event_queue=file_event_queue,
            force_destroy=force_destroy,
            force_update=force_update,
            id=id,
            isolation_mode=isolation_mode,
            metastore_id=metastore_id,
            owner=owner,
            read_only=read_only,
            skip_validation=skip_validation,
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
        '''Generates CDKTF code for importing a ExternalLocation resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ExternalLocation to import.
        :param import_from_id: The id of the existing ExternalLocation that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ExternalLocation to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b487c903c5e96ca29e0f565c7403f37bb181c84ee46528cec526cc2c8d115cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEncryptionDetails")
    def put_encryption_details(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union["ExternalLocationEncryptionDetailsSseEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#sse_encryption_details ExternalLocation#sse_encryption_details}
        '''
        value = ExternalLocationEncryptionDetails(
            sse_encryption_details=sse_encryption_details
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionDetails", [value]))

    @jsii.member(jsii_name="putFileEventQueue")
    def put_file_event_queue(
        self,
        *,
        managed_aqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_pubsub: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_sqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_aqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_pubsub: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_sqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param managed_aqs: managed_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_aqs ExternalLocation#managed_aqs}
        :param managed_pubsub: managed_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_pubsub ExternalLocation#managed_pubsub}
        :param managed_sqs: managed_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_sqs ExternalLocation#managed_sqs}
        :param provided_aqs: provided_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_aqs ExternalLocation#provided_aqs}
        :param provided_pubsub: provided_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_pubsub ExternalLocation#provided_pubsub}
        :param provided_sqs: provided_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_sqs ExternalLocation#provided_sqs}
        '''
        value = ExternalLocationFileEventQueue(
            managed_aqs=managed_aqs,
            managed_pubsub=managed_pubsub,
            managed_sqs=managed_sqs,
            provided_aqs=provided_aqs,
            provided_pubsub=provided_pubsub,
            provided_sqs=provided_sqs,
        )

        return typing.cast(None, jsii.invoke(self, "putFileEventQueue", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetEnableFileEvents")
    def reset_enable_file_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableFileEvents", []))

    @jsii.member(jsii_name="resetEncryptionDetails")
    def reset_encryption_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionDetails", []))

    @jsii.member(jsii_name="resetFallback")
    def reset_fallback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallback", []))

    @jsii.member(jsii_name="resetFileEventQueue")
    def reset_file_event_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileEventQueue", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetForceUpdate")
    def reset_force_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceUpdate", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsolationMode")
    def reset_isolation_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsolationMode", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetSkipValidation")
    def reset_skip_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipValidation", []))

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
    @jsii.member(jsii_name="browseOnly")
    def browse_only(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "browseOnly"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="credentialId")
    def credential_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialId"))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetails")
    def encryption_details(self) -> "ExternalLocationEncryptionDetailsOutputReference":
        return typing.cast("ExternalLocationEncryptionDetailsOutputReference", jsii.get(self, "encryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="fileEventQueue")
    def file_event_queue(self) -> "ExternalLocationFileEventQueueOutputReference":
        return typing.cast("ExternalLocationFileEventQueueOutputReference", jsii.get(self, "fileEventQueue"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialNameInput")
    def credential_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "credentialNameInput"))

    @builtins.property
    @jsii.member(jsii_name="enableFileEventsInput")
    def enable_file_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableFileEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionDetailsInput")
    def encryption_details_input(
        self,
    ) -> typing.Optional["ExternalLocationEncryptionDetails"]:
        return typing.cast(typing.Optional["ExternalLocationEncryptionDetails"], jsii.get(self, "encryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackInput")
    def fallback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackInput"))

    @builtins.property
    @jsii.member(jsii_name="fileEventQueueInput")
    def file_event_queue_input(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueue"]:
        return typing.cast(typing.Optional["ExternalLocationFileEventQueue"], jsii.get(self, "fileEventQueueInput"))

    @builtins.property
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="forceUpdateInput")
    def force_update_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceUpdateInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="isolationModeInput")
    def isolation_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "isolationModeInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreIdInput")
    def metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="skipValidationInput")
    def skip_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipValidationInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbfb49855b09fbc840e526c776c84db11e7746b391e96a53c656fcfd73ceeeda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="credentialName")
    def credential_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "credentialName"))

    @credential_name.setter
    def credential_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9b0eb1dd8265a399c7b0def2fd7b4d078ca8970897b22217b4e2f568876098)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentialName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableFileEvents")
    def enable_file_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableFileEvents"))

    @enable_file_events.setter
    def enable_file_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3944d4934480a80ed16ba27a1180c8c9f92bb075f37f1ff2a6628b9facaac814)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableFileEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallback")
    def fallback(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "fallback"))

    @fallback.setter
    def fallback(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5a729906a1815d898702f8869b60ddd928f162b4d36345c7f048af19a676684)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb89ddf8eb08db03cbe6e1348ba4b2464e0ca829cb0679e67ee7f237048cbf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forceUpdate")
    def force_update(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceUpdate"))

    @force_update.setter
    def force_update(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2241dd82e60bf6783d71279c6c37d2f9fd39ff3778511ebaa58fd97cc9fcee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceUpdate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e53faf82a6ee345997b0604f7bed3f4505b605118c5ddd2bfc546a70dea43e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isolationMode")
    def isolation_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "isolationMode"))

    @isolation_mode.setter
    def isolation_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77b114585498a3f886998231a928d05346984af0cac7f92e64061eb946e08f55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isolationMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817858ff24b8d87cf7245b0b5367ffd116b2c331868ea94d6237d78d886cf796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28ad4a34141ad33dad28a49d89dc204bd0b733c9b7cdcdaf6ea87fc6e3547192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19979c41d03eb85dbc5fa83ce271ff7132f30fbdba28a18f247e3aaa45ac4e89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9edadaeb8b58771f21fb736c6d5ec5990e83cec6cb8ff0f977349261aaf4957a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipValidation")
    def skip_validation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "skipValidation"))

    @skip_validation.setter
    def skip_validation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc6e22fb16b97db63d7f3b8f3b957c69192c5c9311a2acfff06693bf07751a9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipValidation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e31ad127868ca7e9d84b4432206c112a3e2e5a0bde9b44c608b3539d81be6e8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "credential_name": "credentialName",
        "name": "name",
        "url": "url",
        "comment": "comment",
        "enable_file_events": "enableFileEvents",
        "encryption_details": "encryptionDetails",
        "fallback": "fallback",
        "file_event_queue": "fileEventQueue",
        "force_destroy": "forceDestroy",
        "force_update": "forceUpdate",
        "id": "id",
        "isolation_mode": "isolationMode",
        "metastore_id": "metastoreId",
        "owner": "owner",
        "read_only": "readOnly",
        "skip_validation": "skipValidation",
    },
)
class ExternalLocationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        credential_name: builtins.str,
        name: builtins.str,
        url: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_details: typing.Optional[typing.Union["ExternalLocationEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
        fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        file_event_queue: typing.Optional[typing.Union["ExternalLocationFileEventQueue", typing.Dict[builtins.str, typing.Any]]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        isolation_mode: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param credential_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#credential_name ExternalLocation#credential_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#name ExternalLocation#name}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#url ExternalLocation#url}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#comment ExternalLocation#comment}.
        :param enable_file_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#enable_file_events ExternalLocation#enable_file_events}.
        :param encryption_details: encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#encryption_details ExternalLocation#encryption_details}
        :param fallback: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#fallback ExternalLocation#fallback}.
        :param file_event_queue: file_event_queue block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#file_event_queue ExternalLocation#file_event_queue}
        :param force_destroy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_destroy ExternalLocation#force_destroy}.
        :param force_update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_update ExternalLocation#force_update}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#id ExternalLocation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param isolation_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#isolation_mode ExternalLocation#isolation_mode}.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#metastore_id ExternalLocation#metastore_id}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#owner ExternalLocation#owner}.
        :param read_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#read_only ExternalLocation#read_only}.
        :param skip_validation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#skip_validation ExternalLocation#skip_validation}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(encryption_details, dict):
            encryption_details = ExternalLocationEncryptionDetails(**encryption_details)
        if isinstance(file_event_queue, dict):
            file_event_queue = ExternalLocationFileEventQueue(**file_event_queue)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0544337dc68b7c3c56f39e14db84cd1129a07627c0f491bb48227f8642ce62df)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument credential_name", value=credential_name, expected_type=type_hints["credential_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument enable_file_events", value=enable_file_events, expected_type=type_hints["enable_file_events"])
            check_type(argname="argument encryption_details", value=encryption_details, expected_type=type_hints["encryption_details"])
            check_type(argname="argument fallback", value=fallback, expected_type=type_hints["fallback"])
            check_type(argname="argument file_event_queue", value=file_event_queue, expected_type=type_hints["file_event_queue"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument force_update", value=force_update, expected_type=type_hints["force_update"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument isolation_mode", value=isolation_mode, expected_type=type_hints["isolation_mode"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument read_only", value=read_only, expected_type=type_hints["read_only"])
            check_type(argname="argument skip_validation", value=skip_validation, expected_type=type_hints["skip_validation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "credential_name": credential_name,
            "name": name,
            "url": url,
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
        if comment is not None:
            self._values["comment"] = comment
        if enable_file_events is not None:
            self._values["enable_file_events"] = enable_file_events
        if encryption_details is not None:
            self._values["encryption_details"] = encryption_details
        if fallback is not None:
            self._values["fallback"] = fallback
        if file_event_queue is not None:
            self._values["file_event_queue"] = file_event_queue
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if force_update is not None:
            self._values["force_update"] = force_update
        if id is not None:
            self._values["id"] = id
        if isolation_mode is not None:
            self._values["isolation_mode"] = isolation_mode
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if owner is not None:
            self._values["owner"] = owner
        if read_only is not None:
            self._values["read_only"] = read_only
        if skip_validation is not None:
            self._values["skip_validation"] = skip_validation

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
    def credential_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#credential_name ExternalLocation#credential_name}.'''
        result = self._values.get("credential_name")
        assert result is not None, "Required property 'credential_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#name ExternalLocation#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#url ExternalLocation#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#comment ExternalLocation#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_file_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#enable_file_events ExternalLocation#enable_file_events}.'''
        result = self._values.get("enable_file_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_details(
        self,
    ) -> typing.Optional["ExternalLocationEncryptionDetails"]:
        '''encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#encryption_details ExternalLocation#encryption_details}
        '''
        result = self._values.get("encryption_details")
        return typing.cast(typing.Optional["ExternalLocationEncryptionDetails"], result)

    @builtins.property
    def fallback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#fallback ExternalLocation#fallback}.'''
        result = self._values.get("fallback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def file_event_queue(self) -> typing.Optional["ExternalLocationFileEventQueue"]:
        '''file_event_queue block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#file_event_queue ExternalLocation#file_event_queue}
        '''
        result = self._values.get("file_event_queue")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueue"], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_destroy ExternalLocation#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#force_update ExternalLocation#force_update}.'''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#id ExternalLocation#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def isolation_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#isolation_mode ExternalLocation#isolation_mode}.'''
        result = self._values.get("isolation_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#metastore_id ExternalLocation#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#owner ExternalLocation#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#read_only ExternalLocation#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def skip_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#skip_validation ExternalLocation#skip_validation}.'''
        result = self._values.get("skip_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"sse_encryption_details": "sseEncryptionDetails"},
)
class ExternalLocationEncryptionDetails:
    def __init__(
        self,
        *,
        sse_encryption_details: typing.Optional[typing.Union["ExternalLocationEncryptionDetailsSseEncryptionDetails", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param sse_encryption_details: sse_encryption_details block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#sse_encryption_details ExternalLocation#sse_encryption_details}
        '''
        if isinstance(sse_encryption_details, dict):
            sse_encryption_details = ExternalLocationEncryptionDetailsSseEncryptionDetails(**sse_encryption_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b494777d83b0d7be0719b63f1dfdb9818d90f1beee9c59dd750dd656c365cd3)
            check_type(argname="argument sse_encryption_details", value=sse_encryption_details, expected_type=type_hints["sse_encryption_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sse_encryption_details is not None:
            self._values["sse_encryption_details"] = sse_encryption_details

    @builtins.property
    def sse_encryption_details(
        self,
    ) -> typing.Optional["ExternalLocationEncryptionDetailsSseEncryptionDetails"]:
        '''sse_encryption_details block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#sse_encryption_details ExternalLocation#sse_encryption_details}
        '''
        result = self._values.get("sse_encryption_details")
        return typing.cast(typing.Optional["ExternalLocationEncryptionDetailsSseEncryptionDetails"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3bea3f61673ebd42cc3d9377b9b4f9bfcf1ffbf87ffc1c25ccabda02cd57f55)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSseEncryptionDetails")
    def put_sse_encryption_details(
        self,
        *,
        algorithm: typing.Optional[builtins.str] = None,
        aws_kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#algorithm ExternalLocation#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#aws_kms_key_arn ExternalLocation#aws_kms_key_arn}.
        '''
        value = ExternalLocationEncryptionDetailsSseEncryptionDetails(
            algorithm=algorithm, aws_kms_key_arn=aws_kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putSseEncryptionDetails", [value]))

    @jsii.member(jsii_name="resetSseEncryptionDetails")
    def reset_sse_encryption_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseEncryptionDetails", []))

    @builtins.property
    @jsii.member(jsii_name="sseEncryptionDetails")
    def sse_encryption_details(
        self,
    ) -> "ExternalLocationEncryptionDetailsSseEncryptionDetailsOutputReference":
        return typing.cast("ExternalLocationEncryptionDetailsSseEncryptionDetailsOutputReference", jsii.get(self, "sseEncryptionDetails"))

    @builtins.property
    @jsii.member(jsii_name="sseEncryptionDetailsInput")
    def sse_encryption_details_input(
        self,
    ) -> typing.Optional["ExternalLocationEncryptionDetailsSseEncryptionDetails"]:
        return typing.cast(typing.Optional["ExternalLocationEncryptionDetailsSseEncryptionDetails"], jsii.get(self, "sseEncryptionDetailsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ExternalLocationEncryptionDetails]:
        return typing.cast(typing.Optional[ExternalLocationEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cf7bdc0df4599c7ca2408a4e784d3943b89886082368394fcc3b2b86a66710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationEncryptionDetailsSseEncryptionDetails",
    jsii_struct_bases=[],
    name_mapping={"algorithm": "algorithm", "aws_kms_key_arn": "awsKmsKeyArn"},
)
class ExternalLocationEncryptionDetailsSseEncryptionDetails:
    def __init__(
        self,
        *,
        algorithm: typing.Optional[builtins.str] = None,
        aws_kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#algorithm ExternalLocation#algorithm}.
        :param aws_kms_key_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#aws_kms_key_arn ExternalLocation#aws_kms_key_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02ce782e23c6e7ba8a752fb3b477b4e6e945cdac6be3c9577bf4da8479d66d07)
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument aws_kms_key_arn", value=aws_kms_key_arn, expected_type=type_hints["aws_kms_key_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if aws_kms_key_arn is not None:
            self._values["aws_kms_key_arn"] = aws_kms_key_arn

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#algorithm ExternalLocation#algorithm}.'''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#aws_kms_key_arn ExternalLocation#aws_kms_key_arn}.'''
        result = self._values.get("aws_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationEncryptionDetailsSseEncryptionDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationEncryptionDetailsSseEncryptionDetailsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationEncryptionDetailsSseEncryptionDetailsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb259f54559c3ec5ce4b424bf0e2ee5b304d48ad4413ceb1f35b0324646d9e88)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetAwsKmsKeyArn")
    def reset_aws_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsKmsKeyArn", []))

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="awsKmsKeyArnInput")
    def aws_kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsKmsKeyArnInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b265df99d871418d50b6472537adabd2c3f1b9870544f58cd661f68512b40902)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsKmsKeyArn")
    def aws_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsKmsKeyArn"))

    @aws_kms_key_arn.setter
    def aws_kms_key_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b9b5646eebf7d663f4908ca9adb8f8e1fb876f4710aad78abcb7b4920b93d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsKmsKeyArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationEncryptionDetailsSseEncryptionDetails]:
        return typing.cast(typing.Optional[ExternalLocationEncryptionDetailsSseEncryptionDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationEncryptionDetailsSseEncryptionDetails],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea3884d05d44293c5e3f6c390d482d2f10ef82b6ea90cad37d9e1b66b6fab3aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueue",
    jsii_struct_bases=[],
    name_mapping={
        "managed_aqs": "managedAqs",
        "managed_pubsub": "managedPubsub",
        "managed_sqs": "managedSqs",
        "provided_aqs": "providedAqs",
        "provided_pubsub": "providedPubsub",
        "provided_sqs": "providedSqs",
    },
)
class ExternalLocationFileEventQueue:
    def __init__(
        self,
        *,
        managed_aqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_pubsub: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_sqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueManagedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_aqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedAqs", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_pubsub: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedPubsub", typing.Dict[builtins.str, typing.Any]]] = None,
        provided_sqs: typing.Optional[typing.Union["ExternalLocationFileEventQueueProvidedSqs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param managed_aqs: managed_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_aqs ExternalLocation#managed_aqs}
        :param managed_pubsub: managed_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_pubsub ExternalLocation#managed_pubsub}
        :param managed_sqs: managed_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_sqs ExternalLocation#managed_sqs}
        :param provided_aqs: provided_aqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_aqs ExternalLocation#provided_aqs}
        :param provided_pubsub: provided_pubsub block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_pubsub ExternalLocation#provided_pubsub}
        :param provided_sqs: provided_sqs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_sqs ExternalLocation#provided_sqs}
        '''
        if isinstance(managed_aqs, dict):
            managed_aqs = ExternalLocationFileEventQueueManagedAqs(**managed_aqs)
        if isinstance(managed_pubsub, dict):
            managed_pubsub = ExternalLocationFileEventQueueManagedPubsub(**managed_pubsub)
        if isinstance(managed_sqs, dict):
            managed_sqs = ExternalLocationFileEventQueueManagedSqs(**managed_sqs)
        if isinstance(provided_aqs, dict):
            provided_aqs = ExternalLocationFileEventQueueProvidedAqs(**provided_aqs)
        if isinstance(provided_pubsub, dict):
            provided_pubsub = ExternalLocationFileEventQueueProvidedPubsub(**provided_pubsub)
        if isinstance(provided_sqs, dict):
            provided_sqs = ExternalLocationFileEventQueueProvidedSqs(**provided_sqs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9f234182f59d4be586ca3b3a46ce6ff1dd23eb81fbab106f6e75bc6f6ff5740)
            check_type(argname="argument managed_aqs", value=managed_aqs, expected_type=type_hints["managed_aqs"])
            check_type(argname="argument managed_pubsub", value=managed_pubsub, expected_type=type_hints["managed_pubsub"])
            check_type(argname="argument managed_sqs", value=managed_sqs, expected_type=type_hints["managed_sqs"])
            check_type(argname="argument provided_aqs", value=provided_aqs, expected_type=type_hints["provided_aqs"])
            check_type(argname="argument provided_pubsub", value=provided_pubsub, expected_type=type_hints["provided_pubsub"])
            check_type(argname="argument provided_sqs", value=provided_sqs, expected_type=type_hints["provided_sqs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed_aqs is not None:
            self._values["managed_aqs"] = managed_aqs
        if managed_pubsub is not None:
            self._values["managed_pubsub"] = managed_pubsub
        if managed_sqs is not None:
            self._values["managed_sqs"] = managed_sqs
        if provided_aqs is not None:
            self._values["provided_aqs"] = provided_aqs
        if provided_pubsub is not None:
            self._values["provided_pubsub"] = provided_pubsub
        if provided_sqs is not None:
            self._values["provided_sqs"] = provided_sqs

    @builtins.property
    def managed_aqs(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueManagedAqs"]:
        '''managed_aqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_aqs ExternalLocation#managed_aqs}
        '''
        result = self._values.get("managed_aqs")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueManagedAqs"], result)

    @builtins.property
    def managed_pubsub(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueManagedPubsub"]:
        '''managed_pubsub block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_pubsub ExternalLocation#managed_pubsub}
        '''
        result = self._values.get("managed_pubsub")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueManagedPubsub"], result)

    @builtins.property
    def managed_sqs(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueManagedSqs"]:
        '''managed_sqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#managed_sqs ExternalLocation#managed_sqs}
        '''
        result = self._values.get("managed_sqs")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueManagedSqs"], result)

    @builtins.property
    def provided_aqs(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedAqs"]:
        '''provided_aqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_aqs ExternalLocation#provided_aqs}
        '''
        result = self._values.get("provided_aqs")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedAqs"], result)

    @builtins.property
    def provided_pubsub(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedPubsub"]:
        '''provided_pubsub block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_pubsub ExternalLocation#provided_pubsub}
        '''
        result = self._values.get("provided_pubsub")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedPubsub"], result)

    @builtins.property
    def provided_sqs(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedSqs"]:
        '''provided_sqs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#provided_sqs ExternalLocation#provided_sqs}
        '''
        result = self._values.get("provided_sqs")
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedSqs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedAqs",
    jsii_struct_bases=[],
    name_mapping={
        "resource_group": "resourceGroup",
        "subscription_id": "subscriptionId",
        "queue_url": "queueUrl",
    },
)
class ExternalLocationFileEventQueueManagedAqs:
    def __init__(
        self,
        *,
        resource_group: builtins.str,
        subscription_id: builtins.str,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f700a97a4a956369ec45385c4e3fffdaad8e46aacf53447e9a9def0feec3f95)
            check_type(argname="argument resource_group", value=resource_group, expected_type=type_hints["resource_group"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource_group": resource_group,
            "subscription_id": subscription_id,
        }
        if queue_url is not None:
            self._values["queue_url"] = queue_url

    @builtins.property
    def resource_group(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.'''
        result = self._values.get("resource_group")
        assert result is not None, "Required property 'resource_group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscription_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.'''
        result = self._values.get("subscription_id")
        assert result is not None, "Required property 'subscription_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueManagedAqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueManagedAqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedAqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__649139bc976ba4d01fbb88edff0bf387219c7b0771b766e1442752c7b049c900)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupInput")
    def resource_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5568b75c4323395364d68019eb612097ae48507fd615576551e2c8110aafdc37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroup")
    def resource_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroup"))

    @resource_group.setter
    def resource_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec263eb0f9dee7e899a3de86b39ddbe632398d7846c2be37dddbb425ef2acfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d32432bde7a636c8ef10808a1fc7994caa48a10f322dad6b7c395e0f2d186e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedAqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedAqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueManagedAqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4628f40db00af34fdbad52276a097570cb3b194d4543a3f75bc56718ea0e1c76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedPubsub",
    jsii_struct_bases=[],
    name_mapping={"subscription_name": "subscriptionName"},
)
class ExternalLocationFileEventQueueManagedPubsub:
    def __init__(
        self,
        *,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5464d35be07d44072e158a94d287d88840b9d06c8578490d236082c6cef4378)
            check_type(argname="argument subscription_name", value=subscription_name, expected_type=type_hints["subscription_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if subscription_name is not None:
            self._values["subscription_name"] = subscription_name

    @builtins.property
    def subscription_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.'''
        result = self._values.get("subscription_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueManagedPubsub(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueManagedPubsubOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedPubsubOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b4542af3e56a31e408b53c862d3e404f855b3a73c8e91d52b8df75a7a5fbd95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSubscriptionName")
    def reset_subscription_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionName", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionNameInput")
    def subscription_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionName"))

    @subscription_name.setter
    def subscription_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1b6900f335d469936c54500d02e81fa3525d12abfba24985f391fa2898b39ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedPubsub]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedPubsub], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueManagedPubsub],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70cf398fa26d0efbe3dd5198d2e93035b8e2ee62e40d894d762bb50763e83384)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedSqs",
    jsii_struct_bases=[],
    name_mapping={"queue_url": "queueUrl"},
)
class ExternalLocationFileEventQueueManagedSqs:
    def __init__(self, *, queue_url: typing.Optional[builtins.str] = None) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3fed02477e52ff8da4e08cc3472f86801f0fff3147fa41361c4597f2d9857da)
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if queue_url is not None:
            self._values["queue_url"] = queue_url

    @builtins.property
    def queue_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueManagedSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueManagedSqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueManagedSqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3db82782b57b85a58cbe86324a04c869a489b0fe50f44ecc5315cd7b49a4bf87)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetQueueUrl")
    def reset_queue_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueueUrl", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b261b91af9a9c26361ac53de67961ea43ab24e2ef2407115457d165cad946298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedSqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedSqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueManagedSqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71fdbb5b303209addba427a870459439d171792ac075d4c81b583cfc290c12bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ExternalLocationFileEventQueueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bb978c168069d88c8ae029c5fadbdd62553e9c6c4adff05913d261fccc3dbad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putManagedAqs")
    def put_managed_aqs(
        self,
        *,
        resource_group: builtins.str,
        subscription_id: builtins.str,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        value = ExternalLocationFileEventQueueManagedAqs(
            resource_group=resource_group,
            subscription_id=subscription_id,
            queue_url=queue_url,
        )

        return typing.cast(None, jsii.invoke(self, "putManagedAqs", [value]))

    @jsii.member(jsii_name="putManagedPubsub")
    def put_managed_pubsub(
        self,
        *,
        subscription_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.
        '''
        value = ExternalLocationFileEventQueueManagedPubsub(
            subscription_name=subscription_name
        )

        return typing.cast(None, jsii.invoke(self, "putManagedPubsub", [value]))

    @jsii.member(jsii_name="putManagedSqs")
    def put_managed_sqs(
        self,
        *,
        queue_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        value = ExternalLocationFileEventQueueManagedSqs(queue_url=queue_url)

        return typing.cast(None, jsii.invoke(self, "putManagedSqs", [value]))

    @jsii.member(jsii_name="putProvidedAqs")
    def put_provided_aqs(
        self,
        *,
        queue_url: builtins.str,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.
        '''
        value = ExternalLocationFileEventQueueProvidedAqs(
            queue_url=queue_url,
            resource_group=resource_group,
            subscription_id=subscription_id,
        )

        return typing.cast(None, jsii.invoke(self, "putProvidedAqs", [value]))

    @jsii.member(jsii_name="putProvidedPubsub")
    def put_provided_pubsub(self, *, subscription_name: builtins.str) -> None:
        '''
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.
        '''
        value = ExternalLocationFileEventQueueProvidedPubsub(
            subscription_name=subscription_name
        )

        return typing.cast(None, jsii.invoke(self, "putProvidedPubsub", [value]))

    @jsii.member(jsii_name="putProvidedSqs")
    def put_provided_sqs(self, *, queue_url: builtins.str) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        value = ExternalLocationFileEventQueueProvidedSqs(queue_url=queue_url)

        return typing.cast(None, jsii.invoke(self, "putProvidedSqs", [value]))

    @jsii.member(jsii_name="resetManagedAqs")
    def reset_managed_aqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedAqs", []))

    @jsii.member(jsii_name="resetManagedPubsub")
    def reset_managed_pubsub(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedPubsub", []))

    @jsii.member(jsii_name="resetManagedSqs")
    def reset_managed_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedSqs", []))

    @jsii.member(jsii_name="resetProvidedAqs")
    def reset_provided_aqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedAqs", []))

    @jsii.member(jsii_name="resetProvidedPubsub")
    def reset_provided_pubsub(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedPubsub", []))

    @jsii.member(jsii_name="resetProvidedSqs")
    def reset_provided_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvidedSqs", []))

    @builtins.property
    @jsii.member(jsii_name="managedAqs")
    def managed_aqs(self) -> ExternalLocationFileEventQueueManagedAqsOutputReference:
        return typing.cast(ExternalLocationFileEventQueueManagedAqsOutputReference, jsii.get(self, "managedAqs"))

    @builtins.property
    @jsii.member(jsii_name="managedPubsub")
    def managed_pubsub(
        self,
    ) -> ExternalLocationFileEventQueueManagedPubsubOutputReference:
        return typing.cast(ExternalLocationFileEventQueueManagedPubsubOutputReference, jsii.get(self, "managedPubsub"))

    @builtins.property
    @jsii.member(jsii_name="managedSqs")
    def managed_sqs(self) -> ExternalLocationFileEventQueueManagedSqsOutputReference:
        return typing.cast(ExternalLocationFileEventQueueManagedSqsOutputReference, jsii.get(self, "managedSqs"))

    @builtins.property
    @jsii.member(jsii_name="providedAqs")
    def provided_aqs(
        self,
    ) -> "ExternalLocationFileEventQueueProvidedAqsOutputReference":
        return typing.cast("ExternalLocationFileEventQueueProvidedAqsOutputReference", jsii.get(self, "providedAqs"))

    @builtins.property
    @jsii.member(jsii_name="providedPubsub")
    def provided_pubsub(
        self,
    ) -> "ExternalLocationFileEventQueueProvidedPubsubOutputReference":
        return typing.cast("ExternalLocationFileEventQueueProvidedPubsubOutputReference", jsii.get(self, "providedPubsub"))

    @builtins.property
    @jsii.member(jsii_name="providedSqs")
    def provided_sqs(
        self,
    ) -> "ExternalLocationFileEventQueueProvidedSqsOutputReference":
        return typing.cast("ExternalLocationFileEventQueueProvidedSqsOutputReference", jsii.get(self, "providedSqs"))

    @builtins.property
    @jsii.member(jsii_name="managedAqsInput")
    def managed_aqs_input(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedAqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedAqs], jsii.get(self, "managedAqsInput"))

    @builtins.property
    @jsii.member(jsii_name="managedPubsubInput")
    def managed_pubsub_input(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedPubsub]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedPubsub], jsii.get(self, "managedPubsubInput"))

    @builtins.property
    @jsii.member(jsii_name="managedSqsInput")
    def managed_sqs_input(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueManagedSqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueManagedSqs], jsii.get(self, "managedSqsInput"))

    @builtins.property
    @jsii.member(jsii_name="providedAqsInput")
    def provided_aqs_input(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedAqs"]:
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedAqs"], jsii.get(self, "providedAqsInput"))

    @builtins.property
    @jsii.member(jsii_name="providedPubsubInput")
    def provided_pubsub_input(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedPubsub"]:
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedPubsub"], jsii.get(self, "providedPubsubInput"))

    @builtins.property
    @jsii.member(jsii_name="providedSqsInput")
    def provided_sqs_input(
        self,
    ) -> typing.Optional["ExternalLocationFileEventQueueProvidedSqs"]:
        return typing.cast(typing.Optional["ExternalLocationFileEventQueueProvidedSqs"], jsii.get(self, "providedSqsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ExternalLocationFileEventQueue]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbfc86566646080e3f18bb8d50255670b61bc0a8b509dd48e63b71db0bd9b6d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedAqs",
    jsii_struct_bases=[],
    name_mapping={
        "queue_url": "queueUrl",
        "resource_group": "resourceGroup",
        "subscription_id": "subscriptionId",
    },
)
class ExternalLocationFileEventQueueProvidedAqs:
    def __init__(
        self,
        *,
        queue_url: builtins.str,
        resource_group: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        :param resource_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e787298c71fec981e0a627aa66138a80f8efb5f9d651e6fc6edb98b79d84164)
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
            check_type(argname="argument resource_group", value=resource_group, expected_type=type_hints["resource_group"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "queue_url": queue_url,
        }
        if resource_group is not None:
            self._values["resource_group"] = resource_group
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id

    @builtins.property
    def queue_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        assert result is not None, "Required property 'queue_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#resource_group ExternalLocation#resource_group}.'''
        result = self._values.get("resource_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_id ExternalLocation#subscription_id}.'''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueProvidedAqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueProvidedAqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedAqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be6dc609e081165395dd987b0c6ae00e6845a4e2e7bba0c7dd1cebf09d4f571b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetResourceGroup")
    def reset_resource_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroup", []))

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupInput")
    def resource_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13da38db4c1bd9971224163979e498d932ccad3e41c33f46e3cd7cda8e36c2e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroup")
    def resource_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroup"))

    @resource_group.setter
    def resource_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be2aeed3809fa2fd1ee530083a121daa718ce885fb050e5f7b15cbacd397eb09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4e5409a51cd6416cb7fe4c4121a85cf2ef77dbdae017985534589463581a49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueProvidedAqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueProvidedAqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueProvidedAqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67bc9476abc30d25e2183e3a3a47314cb9021b25c078c8345abf7ce735792db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedPubsub",
    jsii_struct_bases=[],
    name_mapping={"subscription_name": "subscriptionName"},
)
class ExternalLocationFileEventQueueProvidedPubsub:
    def __init__(self, *, subscription_name: builtins.str) -> None:
        '''
        :param subscription_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955ec289ae9b25d89dcaebfa39e9d1aa827192da268ae5afc547833ee01aed0a)
            check_type(argname="argument subscription_name", value=subscription_name, expected_type=type_hints["subscription_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subscription_name": subscription_name,
        }

    @builtins.property
    def subscription_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#subscription_name ExternalLocation#subscription_name}.'''
        result = self._values.get("subscription_name")
        assert result is not None, "Required property 'subscription_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueProvidedPubsub(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueProvidedPubsubOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedPubsubOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e51fb160b0604c3533571614f34f9e05f988f6d7a4c45ca3c6d2e183de83ac57)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionNameInput")
    def subscription_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionName"))

    @subscription_name.setter
    def subscription_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54529ce8ac9bcdc4238d42b177672cbefb74c9146805e23b33fd59192354515d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueProvidedPubsub]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueProvidedPubsub], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueProvidedPubsub],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7ede5d99ef424ca44f174a32e7553cedcc26b816c987af81ac0c1bb98145452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedSqs",
    jsii_struct_bases=[],
    name_mapping={"queue_url": "queueUrl"},
)
class ExternalLocationFileEventQueueProvidedSqs:
    def __init__(self, *, queue_url: builtins.str) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6dde4301c7fd1aa84802497113102794113415725aa7864f60a5da2a47d4690)
            check_type(argname="argument queue_url", value=queue_url, expected_type=type_hints["queue_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "queue_url": queue_url,
        }

    @builtins.property
    def queue_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/external_location#queue_url ExternalLocation#queue_url}.'''
        result = self._values.get("queue_url")
        assert result is not None, "Required property 'queue_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalLocationFileEventQueueProvidedSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalLocationFileEventQueueProvidedSqsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.externalLocation.ExternalLocationFileEventQueueProvidedSqsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b50081c22288940f62fba7889a6b07aa5ce61e97f00cb12dcc2c72f703da75e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="managedResourceId")
    def managed_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedResourceId"))

    @builtins.property
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__197bd62ac95caa57c56758c82bc729c629019dd2790a1c7cd9ea72d58cd5bb3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queueUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ExternalLocationFileEventQueueProvidedSqs]:
        return typing.cast(typing.Optional[ExternalLocationFileEventQueueProvidedSqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ExternalLocationFileEventQueueProvidedSqs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0653ba725c99d893df972e914a6a7fb009919574072441a53b870614a798869)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ExternalLocation",
    "ExternalLocationConfig",
    "ExternalLocationEncryptionDetails",
    "ExternalLocationEncryptionDetailsOutputReference",
    "ExternalLocationEncryptionDetailsSseEncryptionDetails",
    "ExternalLocationEncryptionDetailsSseEncryptionDetailsOutputReference",
    "ExternalLocationFileEventQueue",
    "ExternalLocationFileEventQueueManagedAqs",
    "ExternalLocationFileEventQueueManagedAqsOutputReference",
    "ExternalLocationFileEventQueueManagedPubsub",
    "ExternalLocationFileEventQueueManagedPubsubOutputReference",
    "ExternalLocationFileEventQueueManagedSqs",
    "ExternalLocationFileEventQueueManagedSqsOutputReference",
    "ExternalLocationFileEventQueueOutputReference",
    "ExternalLocationFileEventQueueProvidedAqs",
    "ExternalLocationFileEventQueueProvidedAqsOutputReference",
    "ExternalLocationFileEventQueueProvidedPubsub",
    "ExternalLocationFileEventQueueProvidedPubsubOutputReference",
    "ExternalLocationFileEventQueueProvidedSqs",
    "ExternalLocationFileEventQueueProvidedSqsOutputReference",
]

publication.publish()

def _typecheckingstub__7366cd3e0f3652d837eb42745a814fa1e20ee0a42261b2fa98aa1a946825cc7e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    credential_name: builtins.str,
    name: builtins.str,
    url: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_details: typing.Optional[typing.Union[ExternalLocationEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    file_event_queue: typing.Optional[typing.Union[ExternalLocationFileEventQueue, typing.Dict[builtins.str, typing.Any]]] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    isolation_mode: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__6b487c903c5e96ca29e0f565c7403f37bb181c84ee46528cec526cc2c8d115cd(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbfb49855b09fbc840e526c776c84db11e7746b391e96a53c656fcfd73ceeeda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9b0eb1dd8265a399c7b0def2fd7b4d078ca8970897b22217b4e2f568876098(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3944d4934480a80ed16ba27a1180c8c9f92bb075f37f1ff2a6628b9facaac814(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5a729906a1815d898702f8869b60ddd928f162b4d36345c7f048af19a676684(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb89ddf8eb08db03cbe6e1348ba4b2464e0ca829cb0679e67ee7f237048cbf5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2241dd82e60bf6783d71279c6c37d2f9fd39ff3778511ebaa58fd97cc9fcee7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e53faf82a6ee345997b0604f7bed3f4505b605118c5ddd2bfc546a70dea43e55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77b114585498a3f886998231a928d05346984af0cac7f92e64061eb946e08f55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817858ff24b8d87cf7245b0b5367ffd116b2c331868ea94d6237d78d886cf796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ad4a34141ad33dad28a49d89dc204bd0b733c9b7cdcdaf6ea87fc6e3547192(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19979c41d03eb85dbc5fa83ce271ff7132f30fbdba28a18f247e3aaa45ac4e89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9edadaeb8b58771f21fb736c6d5ec5990e83cec6cb8ff0f977349261aaf4957a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc6e22fb16b97db63d7f3b8f3b957c69192c5c9311a2acfff06693bf07751a9c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31ad127868ca7e9d84b4432206c112a3e2e5a0bde9b44c608b3539d81be6e8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0544337dc68b7c3c56f39e14db84cd1129a07627c0f491bb48227f8642ce62df(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    credential_name: builtins.str,
    name: builtins.str,
    url: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    enable_file_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_details: typing.Optional[typing.Union[ExternalLocationEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
    fallback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    file_event_queue: typing.Optional[typing.Union[ExternalLocationFileEventQueue, typing.Dict[builtins.str, typing.Any]]] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    isolation_mode: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    read_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b494777d83b0d7be0719b63f1dfdb9818d90f1beee9c59dd750dd656c365cd3(
    *,
    sse_encryption_details: typing.Optional[typing.Union[ExternalLocationEncryptionDetailsSseEncryptionDetails, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3bea3f61673ebd42cc3d9377b9b4f9bfcf1ffbf87ffc1c25ccabda02cd57f55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cf7bdc0df4599c7ca2408a4e784d3943b89886082368394fcc3b2b86a66710(
    value: typing.Optional[ExternalLocationEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02ce782e23c6e7ba8a752fb3b477b4e6e945cdac6be3c9577bf4da8479d66d07(
    *,
    algorithm: typing.Optional[builtins.str] = None,
    aws_kms_key_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb259f54559c3ec5ce4b424bf0e2ee5b304d48ad4413ceb1f35b0324646d9e88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b265df99d871418d50b6472537adabd2c3f1b9870544f58cd661f68512b40902(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b9b5646eebf7d663f4908ca9adb8f8e1fb876f4710aad78abcb7b4920b93d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea3884d05d44293c5e3f6c390d482d2f10ef82b6ea90cad37d9e1b66b6fab3aa(
    value: typing.Optional[ExternalLocationEncryptionDetailsSseEncryptionDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9f234182f59d4be586ca3b3a46ce6ff1dd23eb81fbab106f6e75bc6f6ff5740(
    *,
    managed_aqs: typing.Optional[typing.Union[ExternalLocationFileEventQueueManagedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_pubsub: typing.Optional[typing.Union[ExternalLocationFileEventQueueManagedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_sqs: typing.Optional[typing.Union[ExternalLocationFileEventQueueManagedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_aqs: typing.Optional[typing.Union[ExternalLocationFileEventQueueProvidedAqs, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_pubsub: typing.Optional[typing.Union[ExternalLocationFileEventQueueProvidedPubsub, typing.Dict[builtins.str, typing.Any]]] = None,
    provided_sqs: typing.Optional[typing.Union[ExternalLocationFileEventQueueProvidedSqs, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f700a97a4a956369ec45385c4e3fffdaad8e46aacf53447e9a9def0feec3f95(
    *,
    resource_group: builtins.str,
    subscription_id: builtins.str,
    queue_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__649139bc976ba4d01fbb88edff0bf387219c7b0771b766e1442752c7b049c900(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5568b75c4323395364d68019eb612097ae48507fd615576551e2c8110aafdc37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec263eb0f9dee7e899a3de86b39ddbe632398d7846c2be37dddbb425ef2acfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d32432bde7a636c8ef10808a1fc7994caa48a10f322dad6b7c395e0f2d186e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4628f40db00af34fdbad52276a097570cb3b194d4543a3f75bc56718ea0e1c76(
    value: typing.Optional[ExternalLocationFileEventQueueManagedAqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5464d35be07d44072e158a94d287d88840b9d06c8578490d236082c6cef4378(
    *,
    subscription_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b4542af3e56a31e408b53c862d3e404f855b3a73c8e91d52b8df75a7a5fbd95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1b6900f335d469936c54500d02e81fa3525d12abfba24985f391fa2898b39ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70cf398fa26d0efbe3dd5198d2e93035b8e2ee62e40d894d762bb50763e83384(
    value: typing.Optional[ExternalLocationFileEventQueueManagedPubsub],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3fed02477e52ff8da4e08cc3472f86801f0fff3147fa41361c4597f2d9857da(
    *,
    queue_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db82782b57b85a58cbe86324a04c869a489b0fe50f44ecc5315cd7b49a4bf87(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b261b91af9a9c26361ac53de67961ea43ab24e2ef2407115457d165cad946298(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71fdbb5b303209addba427a870459439d171792ac075d4c81b583cfc290c12bd(
    value: typing.Optional[ExternalLocationFileEventQueueManagedSqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bb978c168069d88c8ae029c5fadbdd62553e9c6c4adff05913d261fccc3dbad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbfc86566646080e3f18bb8d50255670b61bc0a8b509dd48e63b71db0bd9b6d7(
    value: typing.Optional[ExternalLocationFileEventQueue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e787298c71fec981e0a627aa66138a80f8efb5f9d651e6fc6edb98b79d84164(
    *,
    queue_url: builtins.str,
    resource_group: typing.Optional[builtins.str] = None,
    subscription_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be6dc609e081165395dd987b0c6ae00e6845a4e2e7bba0c7dd1cebf09d4f571b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13da38db4c1bd9971224163979e498d932ccad3e41c33f46e3cd7cda8e36c2e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be2aeed3809fa2fd1ee530083a121daa718ce885fb050e5f7b15cbacd397eb09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4e5409a51cd6416cb7fe4c4121a85cf2ef77dbdae017985534589463581a49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67bc9476abc30d25e2183e3a3a47314cb9021b25c078c8345abf7ce735792db(
    value: typing.Optional[ExternalLocationFileEventQueueProvidedAqs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955ec289ae9b25d89dcaebfa39e9d1aa827192da268ae5afc547833ee01aed0a(
    *,
    subscription_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e51fb160b0604c3533571614f34f9e05f988f6d7a4c45ca3c6d2e183de83ac57(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54529ce8ac9bcdc4238d42b177672cbefb74c9146805e23b33fd59192354515d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7ede5d99ef424ca44f174a32e7553cedcc26b816c987af81ac0c1bb98145452(
    value: typing.Optional[ExternalLocationFileEventQueueProvidedPubsub],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6dde4301c7fd1aa84802497113102794113415725aa7864f60a5da2a47d4690(
    *,
    queue_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b50081c22288940f62fba7889a6b07aa5ce61e97f00cb12dcc2c72f703da75e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197bd62ac95caa57c56758c82bc729c629019dd2790a1c7cd9ea72d58cd5bb3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0653ba725c99d893df972e914a6a7fb009919574072441a53b870614a798869(
    value: typing.Optional[ExternalLocationFileEventQueueProvidedSqs],
) -> None:
    """Type checking stubs"""
    pass
