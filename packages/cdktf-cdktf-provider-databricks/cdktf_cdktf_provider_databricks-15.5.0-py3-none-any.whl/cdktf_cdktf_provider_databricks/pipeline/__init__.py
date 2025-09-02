r'''
# `databricks_pipeline`

Refer to the Terraform Registry for docs: [`databricks_pipeline`](https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline).
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


class Pipeline(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.Pipeline",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline databricks_pipeline}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        allow_duplicate_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        catalog: typing.Optional[builtins.str] = None,
        cause: typing.Optional[builtins.str] = None,
        channel: typing.Optional[builtins.str] = None,
        cluster: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineCluster", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        configuration: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        continuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        deployment: typing.Optional[typing.Union["PipelineDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        development: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edition: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Union["PipelineEnvironment", typing.Dict[builtins.str, typing.Any]]] = None,
        event_log: typing.Optional[typing.Union["PipelineEventLog", typing.Dict[builtins.str, typing.Any]]] = None,
        expected_last_modified: typing.Optional[jsii.Number] = None,
        filters: typing.Optional[typing.Union["PipelineFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        gateway_definition: typing.Optional[typing.Union["PipelineGatewayDefinition", typing.Dict[builtins.str, typing.Any]]] = None,
        health: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ingestion_definition: typing.Optional[typing.Union["PipelineIngestionDefinition", typing.Dict[builtins.str, typing.Any]]] = None,
        last_modified: typing.Optional[jsii.Number] = None,
        latest_updates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLatestUpdates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLibrary", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineNotification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        restart_window: typing.Optional[typing.Union["PipelineRestartWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        root_path: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["PipelineRunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        serverless: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        state: typing.Optional[builtins.str] = None,
        storage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["PipelineTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        trigger: typing.Optional[typing.Union["PipelineTrigger", typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline databricks_pipeline} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allow_duplicate_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#allow_duplicate_names Pipeline#allow_duplicate_names}.
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#budget_policy_id Pipeline#budget_policy_id}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.
        :param cause: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cause Pipeline#cause}.
        :param channel: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#channel Pipeline#channel}.
        :param cluster: cluster block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster Pipeline#cluster}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster_id Pipeline#cluster_id}.
        :param configuration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#configuration Pipeline#configuration}.
        :param continuous: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#continuous Pipeline#continuous}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#creator_user_name Pipeline#creator_user_name}.
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deployment Pipeline#deployment}
        :param development: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#development Pipeline#development}.
        :param edition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#edition Pipeline#edition}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#environment Pipeline#environment}
        :param event_log: event_log block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#event_log Pipeline#event_log}
        :param expected_last_modified: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#expected_last_modified Pipeline#expected_last_modified}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#filters Pipeline#filters}
        :param gateway_definition: gateway_definition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_definition Pipeline#gateway_definition}
        :param health: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#health Pipeline#health}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#id Pipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingestion_definition: ingestion_definition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_definition Pipeline#ingestion_definition}
        :param last_modified: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#last_modified Pipeline#last_modified}.
        :param latest_updates: latest_updates block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#latest_updates Pipeline#latest_updates}
        :param library: library block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#library Pipeline#library}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#notification Pipeline#notification}
        :param photon: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#photon Pipeline#photon}.
        :param restart_window: restart_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#restart_window Pipeline#restart_window}
        :param root_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#root_path Pipeline#root_path}.
        :param run_as: run_as block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as Pipeline#run_as}
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as_user_name Pipeline#run_as_user_name}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.
        :param serverless: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#serverless Pipeline#serverless}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#state Pipeline#state}.
        :param storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#storage Pipeline#storage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#tags Pipeline#tags}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#target Pipeline#target}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timeouts Pipeline#timeouts}
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#trigger Pipeline#trigger}
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#url Pipeline#url}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0bf98735978227a74d3563ac743f858b0ee60db9c653153e602bcf484da355f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PipelineConfig(
            allow_duplicate_names=allow_duplicate_names,
            budget_policy_id=budget_policy_id,
            catalog=catalog,
            cause=cause,
            channel=channel,
            cluster=cluster,
            cluster_id=cluster_id,
            configuration=configuration,
            continuous=continuous,
            creator_user_name=creator_user_name,
            deployment=deployment,
            development=development,
            edition=edition,
            environment=environment,
            event_log=event_log,
            expected_last_modified=expected_last_modified,
            filters=filters,
            gateway_definition=gateway_definition,
            health=health,
            id=id,
            ingestion_definition=ingestion_definition,
            last_modified=last_modified,
            latest_updates=latest_updates,
            library=library,
            name=name,
            notification=notification,
            photon=photon,
            restart_window=restart_window,
            root_path=root_path,
            run_as=run_as,
            run_as_user_name=run_as_user_name,
            schema=schema,
            serverless=serverless,
            state=state,
            storage=storage,
            tags=tags,
            target=target,
            timeouts=timeouts,
            trigger=trigger,
            url=url,
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
        '''Generates CDKTF code for importing a Pipeline resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Pipeline to import.
        :param import_from_id: The id of the existing Pipeline that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Pipeline to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e79f98be421668ee66ea6484d27e20efb71e6167145f9f4f52521307895c1e9c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCluster")
    def put_cluster(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineCluster", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__686f058a1524241956419cb676489836151d4f1cbc411aafe6df3f21e8cb497f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCluster", [value]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        *,
        kind: builtins.str,
        metadata_file_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kind Pipeline#kind}.
        :param metadata_file_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#metadata_file_path Pipeline#metadata_file_path}.
        '''
        value = PipelineDeployment(kind=kind, metadata_file_path=metadata_file_path)

        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="putEnvironment")
    def put_environment(
        self,
        *,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param dependencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dependencies Pipeline#dependencies}.
        '''
        value = PipelineEnvironment(dependencies=dependencies)

        return typing.cast(None, jsii.invoke(self, "putEnvironment", [value]))

    @jsii.member(jsii_name="putEventLog")
    def put_event_log(
        self,
        *,
        name: builtins.str,
        catalog: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.
        '''
        value = PipelineEventLog(name=name, catalog=catalog, schema=schema)

        return typing.cast(None, jsii.invoke(self, "putEventLog", [value]))

    @jsii.member(jsii_name="putFilters")
    def put_filters(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude Pipeline#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.
        '''
        value = PipelineFilters(exclude=exclude, include=include)

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="putGatewayDefinition")
    def put_gateway_definition(
        self,
        *,
        connection_name: builtins.str,
        gateway_storage_catalog: builtins.str,
        gateway_storage_schema: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
        gateway_storage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.
        :param gateway_storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_catalog Pipeline#gateway_storage_catalog}.
        :param gateway_storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_schema Pipeline#gateway_storage_schema}.
        :param connection_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_id Pipeline#connection_id}.
        :param gateway_storage_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_name Pipeline#gateway_storage_name}.
        '''
        value = PipelineGatewayDefinition(
            connection_name=connection_name,
            gateway_storage_catalog=gateway_storage_catalog,
            gateway_storage_schema=gateway_storage_schema,
            connection_id=connection_id,
            gateway_storage_name=gateway_storage_name,
        )

        return typing.cast(None, jsii.invoke(self, "putGatewayDefinition", [value]))

    @jsii.member(jsii_name="putIngestionDefinition")
    def put_ingestion_definition(
        self,
        *,
        connection_name: typing.Optional[builtins.str] = None,
        ingestion_gateway_id: typing.Optional[builtins.str] = None,
        objects: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineIngestionDefinitionObjects", typing.Dict[builtins.str, typing.Any]]]]] = None,
        source_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineIngestionDefinitionSourceConfigurations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        source_type: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.
        :param ingestion_gateway_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_gateway_id Pipeline#ingestion_gateway_id}.
        :param objects: objects block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#objects Pipeline#objects}
        :param source_configurations: source_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_configurations Pipeline#source_configurations}
        :param source_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_type Pipeline#source_type}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        value = PipelineIngestionDefinition(
            connection_name=connection_name,
            ingestion_gateway_id=ingestion_gateway_id,
            objects=objects,
            source_configurations=source_configurations,
            source_type=source_type,
            table_configuration=table_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putIngestionDefinition", [value]))

    @jsii.member(jsii_name="putLatestUpdates")
    def put_latest_updates(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLatestUpdates", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca318dc3a600244706ba5c10ccd71acb4a5c04fe891e17bd4373a1ea359c591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLatestUpdates", [value]))

    @jsii.member(jsii_name="putLibrary")
    def put_library(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLibrary", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__718051e6297cf70b4433c1dc18d1514e18bda33aa43b59951fed173deee71445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLibrary", [value]))

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineNotification", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae2ffd87d23f97fff4978ba983ffa8f06b698de24c0d629ea578a2e012f2840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNotification", [value]))

    @jsii.member(jsii_name="putRestartWindow")
    def put_restart_window(
        self,
        *,
        start_hour: jsii.Number,
        days_of_week: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param start_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#start_hour Pipeline#start_hour}.
        :param days_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#days_of_week Pipeline#days_of_week}.
        :param time_zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#time_zone_id Pipeline#time_zone_id}.
        '''
        value = PipelineRestartWindow(
            start_hour=start_hour, days_of_week=days_of_week, time_zone_id=time_zone_id
        )

        return typing.cast(None, jsii.invoke(self, "putRestartWindow", [value]))

    @jsii.member(jsii_name="putRunAs")
    def put_run_as(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#service_principal_name Pipeline#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#user_name Pipeline#user_name}.
        '''
        value = PipelineRunAs(
            service_principal_name=service_principal_name, user_name=user_name
        )

        return typing.cast(None, jsii.invoke(self, "putRunAs", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, default: typing.Optional[builtins.str] = None) -> None:
        '''
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#default Pipeline#default}.
        '''
        value = PipelineTimeouts(default=default)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTrigger")
    def put_trigger(
        self,
        *,
        cron: typing.Optional[typing.Union["PipelineTriggerCron", typing.Dict[builtins.str, typing.Any]]] = None,
        manual: typing.Optional[typing.Union["PipelineTriggerManual", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cron: cron block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cron Pipeline#cron}
        :param manual: manual block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#manual Pipeline#manual}
        '''
        value = PipelineTrigger(cron=cron, manual=manual)

        return typing.cast(None, jsii.invoke(self, "putTrigger", [value]))

    @jsii.member(jsii_name="resetAllowDuplicateNames")
    def reset_allow_duplicate_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowDuplicateNames", []))

    @jsii.member(jsii_name="resetBudgetPolicyId")
    def reset_budget_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBudgetPolicyId", []))

    @jsii.member(jsii_name="resetCatalog")
    def reset_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalog", []))

    @jsii.member(jsii_name="resetCause")
    def reset_cause(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCause", []))

    @jsii.member(jsii_name="resetChannel")
    def reset_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannel", []))

    @jsii.member(jsii_name="resetCluster")
    def reset_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCluster", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetConfiguration")
    def reset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguration", []))

    @jsii.member(jsii_name="resetContinuous")
    def reset_continuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContinuous", []))

    @jsii.member(jsii_name="resetCreatorUserName")
    def reset_creator_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatorUserName", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDevelopment")
    def reset_development(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevelopment", []))

    @jsii.member(jsii_name="resetEdition")
    def reset_edition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEdition", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetEventLog")
    def reset_event_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventLog", []))

    @jsii.member(jsii_name="resetExpectedLastModified")
    def reset_expected_last_modified(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedLastModified", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="resetGatewayDefinition")
    def reset_gateway_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayDefinition", []))

    @jsii.member(jsii_name="resetHealth")
    def reset_health(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealth", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIngestionDefinition")
    def reset_ingestion_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngestionDefinition", []))

    @jsii.member(jsii_name="resetLastModified")
    def reset_last_modified(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastModified", []))

    @jsii.member(jsii_name="resetLatestUpdates")
    def reset_latest_updates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatestUpdates", []))

    @jsii.member(jsii_name="resetLibrary")
    def reset_library(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLibrary", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNotification")
    def reset_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotification", []))

    @jsii.member(jsii_name="resetPhoton")
    def reset_photon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhoton", []))

    @jsii.member(jsii_name="resetRestartWindow")
    def reset_restart_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartWindow", []))

    @jsii.member(jsii_name="resetRootPath")
    def reset_root_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootPath", []))

    @jsii.member(jsii_name="resetRunAs")
    def reset_run_as(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAs", []))

    @jsii.member(jsii_name="resetRunAsUserName")
    def reset_run_as_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunAsUserName", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetServerless")
    def reset_serverless(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerless", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetStorage")
    def reset_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorage", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTrigger")
    def reset_trigger(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrigger", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

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
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> "PipelineClusterList":
        return typing.cast("PipelineClusterList", jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> "PipelineDeploymentOutputReference":
        return typing.cast("PipelineDeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> "PipelineEnvironmentOutputReference":
        return typing.cast("PipelineEnvironmentOutputReference", jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="eventLog")
    def event_log(self) -> "PipelineEventLogOutputReference":
        return typing.cast("PipelineEventLogOutputReference", jsii.get(self, "eventLog"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> "PipelineFiltersOutputReference":
        return typing.cast("PipelineFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="gatewayDefinition")
    def gateway_definition(self) -> "PipelineGatewayDefinitionOutputReference":
        return typing.cast("PipelineGatewayDefinitionOutputReference", jsii.get(self, "gatewayDefinition"))

    @builtins.property
    @jsii.member(jsii_name="ingestionDefinition")
    def ingestion_definition(self) -> "PipelineIngestionDefinitionOutputReference":
        return typing.cast("PipelineIngestionDefinitionOutputReference", jsii.get(self, "ingestionDefinition"))

    @builtins.property
    @jsii.member(jsii_name="latestUpdates")
    def latest_updates(self) -> "PipelineLatestUpdatesList":
        return typing.cast("PipelineLatestUpdatesList", jsii.get(self, "latestUpdates"))

    @builtins.property
    @jsii.member(jsii_name="library")
    def library(self) -> "PipelineLibraryList":
        return typing.cast("PipelineLibraryList", jsii.get(self, "library"))

    @builtins.property
    @jsii.member(jsii_name="notification")
    def notification(self) -> "PipelineNotificationList":
        return typing.cast("PipelineNotificationList", jsii.get(self, "notification"))

    @builtins.property
    @jsii.member(jsii_name="restartWindow")
    def restart_window(self) -> "PipelineRestartWindowOutputReference":
        return typing.cast("PipelineRestartWindowOutputReference", jsii.get(self, "restartWindow"))

    @builtins.property
    @jsii.member(jsii_name="runAs")
    def run_as(self) -> "PipelineRunAsOutputReference":
        return typing.cast("PipelineRunAsOutputReference", jsii.get(self, "runAs"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "PipelineTimeoutsOutputReference":
        return typing.cast("PipelineTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="trigger")
    def trigger(self) -> "PipelineTriggerOutputReference":
        return typing.cast("PipelineTriggerOutputReference", jsii.get(self, "trigger"))

    @builtins.property
    @jsii.member(jsii_name="allowDuplicateNamesInput")
    def allow_duplicate_names_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowDuplicateNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyIdInput")
    def budget_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetPolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="catalogInput")
    def catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogInput"))

    @builtins.property
    @jsii.member(jsii_name="causeInput")
    def cause_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "causeInput"))

    @builtins.property
    @jsii.member(jsii_name="channelInput")
    def channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterInput")
    def cluster_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineCluster"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineCluster"]]], jsii.get(self, "clusterInput"))

    @builtins.property
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "configurationInput"))

    @builtins.property
    @jsii.member(jsii_name="continuousInput")
    def continuous_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "continuousInput"))

    @builtins.property
    @jsii.member(jsii_name="creatorUserNameInput")
    def creator_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creatorUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(self) -> typing.Optional["PipelineDeployment"]:
        return typing.cast(typing.Optional["PipelineDeployment"], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="developmentInput")
    def development_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "developmentInput"))

    @builtins.property
    @jsii.member(jsii_name="editionInput")
    def edition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "editionInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional["PipelineEnvironment"]:
        return typing.cast(typing.Optional["PipelineEnvironment"], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="eventLogInput")
    def event_log_input(self) -> typing.Optional["PipelineEventLog"]:
        return typing.cast(typing.Optional["PipelineEventLog"], jsii.get(self, "eventLogInput"))

    @builtins.property
    @jsii.member(jsii_name="expectedLastModifiedInput")
    def expected_last_modified_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expectedLastModifiedInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["PipelineFilters"]:
        return typing.cast(typing.Optional["PipelineFilters"], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayDefinitionInput")
    def gateway_definition_input(self) -> typing.Optional["PipelineGatewayDefinition"]:
        return typing.cast(typing.Optional["PipelineGatewayDefinition"], jsii.get(self, "gatewayDefinitionInput"))

    @builtins.property
    @jsii.member(jsii_name="healthInput")
    def health_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ingestionDefinitionInput")
    def ingestion_definition_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinition"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinition"], jsii.get(self, "ingestionDefinitionInput"))

    @builtins.property
    @jsii.member(jsii_name="lastModifiedInput")
    def last_modified_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastModifiedInput"))

    @builtins.property
    @jsii.member(jsii_name="latestUpdatesInput")
    def latest_updates_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLatestUpdates"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLatestUpdates"]]], jsii.get(self, "latestUpdatesInput"))

    @builtins.property
    @jsii.member(jsii_name="libraryInput")
    def library_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLibrary"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLibrary"]]], jsii.get(self, "libraryInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationInput")
    def notification_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineNotification"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineNotification"]]], jsii.get(self, "notificationInput"))

    @builtins.property
    @jsii.member(jsii_name="photonInput")
    def photon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "photonInput"))

    @builtins.property
    @jsii.member(jsii_name="restartWindowInput")
    def restart_window_input(self) -> typing.Optional["PipelineRestartWindow"]:
        return typing.cast(typing.Optional["PipelineRestartWindow"], jsii.get(self, "restartWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="rootPathInput")
    def root_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootPathInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsInput")
    def run_as_input(self) -> typing.Optional["PipelineRunAs"]:
        return typing.cast(typing.Optional["PipelineRunAs"], jsii.get(self, "runAsInput"))

    @builtins.property
    @jsii.member(jsii_name="runAsUserNameInput")
    def run_as_user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runAsUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="serverlessInput")
    def serverless_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serverlessInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="storageInput")
    def storage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PipelineTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PipelineTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerInput")
    def trigger_input(self) -> typing.Optional["PipelineTrigger"]:
        return typing.cast(typing.Optional["PipelineTrigger"], jsii.get(self, "triggerInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="allowDuplicateNames")
    def allow_duplicate_names(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowDuplicateNames"))

    @allow_duplicate_names.setter
    def allow_duplicate_names(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc9504f8da036eea33cd9d2fa16e93a946738866c0f20f792eafc46b930f7623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowDuplicateNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="budgetPolicyId")
    def budget_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetPolicyId"))

    @budget_policy_id.setter
    def budget_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8801f174a1eebadd84afd14e643f8df847264825ce3d10d2d51ed9909012fa2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "budgetPolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="catalog")
    def catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalog"))

    @catalog.setter
    def catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62ac2805211275e46dbbeeb48262da2e18af8958f90c77a563416d57d2f8e66f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cause")
    def cause(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cause"))

    @cause.setter
    def cause(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf06f6c0c601c3f3f742350445815f36b0c9a79c21e234dd977622ddfdb781f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cause", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="channel")
    def channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channel"))

    @channel.setter
    def channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38565a30cf245e322d591c06e2a2e27b56dcfea061aa3d6a31ad44f119e2831a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__569c5ec975959b273e537c17b09d80f01e4d3677263ae67fa8917ac2cb6e3fc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d82d6f9c5b4a4b60e61b94a5b9fdcb486145d545ddd39214f47c588d695cf51a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="continuous")
    def continuous(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "continuous"))

    @continuous.setter
    def continuous(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d776bac6cd09f0f317f6e9fe6d7e371df1bcc9ce780b60302c97da1ba9723258)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "continuous", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="creatorUserName")
    def creator_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creatorUserName"))

    @creator_user_name.setter
    def creator_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45ab4cf5ff8025960a032974b2c993b8e6f74bac4f3eb71f45cdfc366dee9ed0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creatorUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="development")
    def development(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "development"))

    @development.setter
    def development(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b7bbbf776ad3ddaf8df1fd8e0bbd5a572dd86c328ee3fd5414edded35871869)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "development", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="edition")
    def edition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "edition"))

    @edition.setter
    def edition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfecfa3fab80f92ee4b1e05c2036a993352ee072593957b5c091181dde1d0843)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "edition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expectedLastModified")
    def expected_last_modified(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expectedLastModified"))

    @expected_last_modified.setter
    def expected_last_modified(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__936c9b1e76ec4feab4ecc032ea16c5064c047f5123fded545325b8b96917ab56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expectedLastModified", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="health")
    def health(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "health"))

    @health.setter
    def health(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f939a28797f941dac3959266dd9919dd59a4855198790407bfa2aace70b5f53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "health", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340a3daffd53a98b8ac2eb1e1814feb8b0cd9b3e219801ebf86069ded5dd83ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastModified"))

    @last_modified.setter
    def last_modified(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afc2fb866b548a23aff8122b2c51572f919a5dffec5080ba8ffcdaf0e3abe9f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastModified", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52914df0ba6a3df04d8e2e4a9793eae1dd3bfe17fdef6941e43dd82cb7dd0e66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="photon")
    def photon(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "photon"))

    @photon.setter
    def photon(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54ce1e56fa768f54ef0ef4788516029aac7b814c759a8167e2e06168aff726e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "photon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootPath")
    def root_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootPath"))

    @root_path.setter
    def root_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f365a53a7af7f1dcf74aaf41eddcbf1d5b1c9166fa9a5f8f8213628f1f76d41f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runAsUserName")
    def run_as_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runAsUserName"))

    @run_as_user_name.setter
    def run_as_user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66f635c1e46ba212487df93c5bec58a6787a1d1cc7066575713957d030c00c1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runAsUserName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__876b9a513ec60441a6a2ed714abb4476a65d8000266eb6d76e64f985ccb62526)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverless")
    def serverless(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serverless"))

    @serverless.setter
    def serverless(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a2d03895dcb1012266dc2e6639332747dd69239a74e4ca375f5923e9212e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverless", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef46bfbec16dfa39a424e12b1a3b10f843f445e4c518845dea517ba795b91ee8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storage")
    def storage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storage"))

    @storage.setter
    def storage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7968488943d1334fb7475d8aede2aa14864369caa904f97b207b50df2c910da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e468de22fefbc9b51274d707874100af970efb96b99699d618e27a30077184b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18fd81aeb2565e470cd54e1852540a156b600d994f43f9504f859c693f097de6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24bb6c29f8c93f29bac732a754dc39bc4917d8ffae142d5e5550981983a9c607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineCluster",
    jsii_struct_bases=[],
    name_mapping={
        "apply_policy_default_values": "applyPolicyDefaultValues",
        "autoscale": "autoscale",
        "aws_attributes": "awsAttributes",
        "azure_attributes": "azureAttributes",
        "cluster_log_conf": "clusterLogConf",
        "custom_tags": "customTags",
        "driver_instance_pool_id": "driverInstancePoolId",
        "driver_node_type_id": "driverNodeTypeId",
        "enable_local_disk_encryption": "enableLocalDiskEncryption",
        "gcp_attributes": "gcpAttributes",
        "init_scripts": "initScripts",
        "instance_pool_id": "instancePoolId",
        "label": "label",
        "node_type_id": "nodeTypeId",
        "num_workers": "numWorkers",
        "policy_id": "policyId",
        "spark_conf": "sparkConf",
        "spark_env_vars": "sparkEnvVars",
        "ssh_public_keys": "sshPublicKeys",
    },
)
class PipelineCluster:
    def __init__(
        self,
        *,
        apply_policy_default_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale: typing.Optional[typing.Union["PipelineClusterAutoscale", typing.Dict[builtins.str, typing.Any]]] = None,
        aws_attributes: typing.Optional[typing.Union["PipelineClusterAwsAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_attributes: typing.Optional[typing.Union["PipelineClusterAzureAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_log_conf: typing.Optional[typing.Union["PipelineClusterClusterLogConf", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        driver_instance_pool_id: typing.Optional[builtins.str] = None,
        driver_node_type_id: typing.Optional[builtins.str] = None,
        enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gcp_attributes: typing.Optional[typing.Union["PipelineClusterGcpAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineClusterInitScripts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_pool_id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        node_type_id: typing.Optional[builtins.str] = None,
        num_workers: typing.Optional[jsii.Number] = None,
        policy_id: typing.Optional[builtins.str] = None,
        spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param apply_policy_default_values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#apply_policy_default_values Pipeline#apply_policy_default_values}.
        :param autoscale: autoscale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#autoscale Pipeline#autoscale}
        :param aws_attributes: aws_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#aws_attributes Pipeline#aws_attributes}
        :param azure_attributes: azure_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#azure_attributes Pipeline#azure_attributes}
        :param cluster_log_conf: cluster_log_conf block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster_log_conf Pipeline#cluster_log_conf}
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#custom_tags Pipeline#custom_tags}.
        :param driver_instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#driver_instance_pool_id Pipeline#driver_instance_pool_id}.
        :param driver_node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#driver_node_type_id Pipeline#driver_node_type_id}.
        :param enable_local_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_local_disk_encryption Pipeline#enable_local_disk_encryption}.
        :param gcp_attributes: gcp_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gcp_attributes Pipeline#gcp_attributes}
        :param init_scripts: init_scripts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#init_scripts Pipeline#init_scripts}
        :param instance_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#instance_pool_id Pipeline#instance_pool_id}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#label Pipeline#label}.
        :param node_type_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#node_type_id Pipeline#node_type_id}.
        :param num_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#num_workers Pipeline#num_workers}.
        :param policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#policy_id Pipeline#policy_id}.
        :param spark_conf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spark_conf Pipeline#spark_conf}.
        :param spark_env_vars: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spark_env_vars Pipeline#spark_env_vars}.
        :param ssh_public_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ssh_public_keys Pipeline#ssh_public_keys}.
        '''
        if isinstance(autoscale, dict):
            autoscale = PipelineClusterAutoscale(**autoscale)
        if isinstance(aws_attributes, dict):
            aws_attributes = PipelineClusterAwsAttributes(**aws_attributes)
        if isinstance(azure_attributes, dict):
            azure_attributes = PipelineClusterAzureAttributes(**azure_attributes)
        if isinstance(cluster_log_conf, dict):
            cluster_log_conf = PipelineClusterClusterLogConf(**cluster_log_conf)
        if isinstance(gcp_attributes, dict):
            gcp_attributes = PipelineClusterGcpAttributes(**gcp_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a33176ebeb01b06e2dc9b6ed97def2da3e6dabd5818a8f26834a7b8e3ceed811)
            check_type(argname="argument apply_policy_default_values", value=apply_policy_default_values, expected_type=type_hints["apply_policy_default_values"])
            check_type(argname="argument autoscale", value=autoscale, expected_type=type_hints["autoscale"])
            check_type(argname="argument aws_attributes", value=aws_attributes, expected_type=type_hints["aws_attributes"])
            check_type(argname="argument azure_attributes", value=azure_attributes, expected_type=type_hints["azure_attributes"])
            check_type(argname="argument cluster_log_conf", value=cluster_log_conf, expected_type=type_hints["cluster_log_conf"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument driver_instance_pool_id", value=driver_instance_pool_id, expected_type=type_hints["driver_instance_pool_id"])
            check_type(argname="argument driver_node_type_id", value=driver_node_type_id, expected_type=type_hints["driver_node_type_id"])
            check_type(argname="argument enable_local_disk_encryption", value=enable_local_disk_encryption, expected_type=type_hints["enable_local_disk_encryption"])
            check_type(argname="argument gcp_attributes", value=gcp_attributes, expected_type=type_hints["gcp_attributes"])
            check_type(argname="argument init_scripts", value=init_scripts, expected_type=type_hints["init_scripts"])
            check_type(argname="argument instance_pool_id", value=instance_pool_id, expected_type=type_hints["instance_pool_id"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument node_type_id", value=node_type_id, expected_type=type_hints["node_type_id"])
            check_type(argname="argument num_workers", value=num_workers, expected_type=type_hints["num_workers"])
            check_type(argname="argument policy_id", value=policy_id, expected_type=type_hints["policy_id"])
            check_type(argname="argument spark_conf", value=spark_conf, expected_type=type_hints["spark_conf"])
            check_type(argname="argument spark_env_vars", value=spark_env_vars, expected_type=type_hints["spark_env_vars"])
            check_type(argname="argument ssh_public_keys", value=ssh_public_keys, expected_type=type_hints["ssh_public_keys"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if apply_policy_default_values is not None:
            self._values["apply_policy_default_values"] = apply_policy_default_values
        if autoscale is not None:
            self._values["autoscale"] = autoscale
        if aws_attributes is not None:
            self._values["aws_attributes"] = aws_attributes
        if azure_attributes is not None:
            self._values["azure_attributes"] = azure_attributes
        if cluster_log_conf is not None:
            self._values["cluster_log_conf"] = cluster_log_conf
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if driver_instance_pool_id is not None:
            self._values["driver_instance_pool_id"] = driver_instance_pool_id
        if driver_node_type_id is not None:
            self._values["driver_node_type_id"] = driver_node_type_id
        if enable_local_disk_encryption is not None:
            self._values["enable_local_disk_encryption"] = enable_local_disk_encryption
        if gcp_attributes is not None:
            self._values["gcp_attributes"] = gcp_attributes
        if init_scripts is not None:
            self._values["init_scripts"] = init_scripts
        if instance_pool_id is not None:
            self._values["instance_pool_id"] = instance_pool_id
        if label is not None:
            self._values["label"] = label
        if node_type_id is not None:
            self._values["node_type_id"] = node_type_id
        if num_workers is not None:
            self._values["num_workers"] = num_workers
        if policy_id is not None:
            self._values["policy_id"] = policy_id
        if spark_conf is not None:
            self._values["spark_conf"] = spark_conf
        if spark_env_vars is not None:
            self._values["spark_env_vars"] = spark_env_vars
        if ssh_public_keys is not None:
            self._values["ssh_public_keys"] = ssh_public_keys

    @builtins.property
    def apply_policy_default_values(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#apply_policy_default_values Pipeline#apply_policy_default_values}.'''
        result = self._values.get("apply_policy_default_values")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autoscale(self) -> typing.Optional["PipelineClusterAutoscale"]:
        '''autoscale block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#autoscale Pipeline#autoscale}
        '''
        result = self._values.get("autoscale")
        return typing.cast(typing.Optional["PipelineClusterAutoscale"], result)

    @builtins.property
    def aws_attributes(self) -> typing.Optional["PipelineClusterAwsAttributes"]:
        '''aws_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#aws_attributes Pipeline#aws_attributes}
        '''
        result = self._values.get("aws_attributes")
        return typing.cast(typing.Optional["PipelineClusterAwsAttributes"], result)

    @builtins.property
    def azure_attributes(self) -> typing.Optional["PipelineClusterAzureAttributes"]:
        '''azure_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#azure_attributes Pipeline#azure_attributes}
        '''
        result = self._values.get("azure_attributes")
        return typing.cast(typing.Optional["PipelineClusterAzureAttributes"], result)

    @builtins.property
    def cluster_log_conf(self) -> typing.Optional["PipelineClusterClusterLogConf"]:
        '''cluster_log_conf block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster_log_conf Pipeline#cluster_log_conf}
        '''
        result = self._values.get("cluster_log_conf")
        return typing.cast(typing.Optional["PipelineClusterClusterLogConf"], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#custom_tags Pipeline#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def driver_instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#driver_instance_pool_id Pipeline#driver_instance_pool_id}.'''
        result = self._values.get("driver_instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#driver_node_type_id Pipeline#driver_node_type_id}.'''
        result = self._values.get("driver_node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_local_disk_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_local_disk_encryption Pipeline#enable_local_disk_encryption}.'''
        result = self._values.get("enable_local_disk_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gcp_attributes(self) -> typing.Optional["PipelineClusterGcpAttributes"]:
        '''gcp_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gcp_attributes Pipeline#gcp_attributes}
        '''
        result = self._values.get("gcp_attributes")
        return typing.cast(typing.Optional["PipelineClusterGcpAttributes"], result)

    @builtins.property
    def init_scripts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineClusterInitScripts"]]]:
        '''init_scripts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#init_scripts Pipeline#init_scripts}
        '''
        result = self._values.get("init_scripts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineClusterInitScripts"]]], result)

    @builtins.property
    def instance_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#instance_pool_id Pipeline#instance_pool_id}.'''
        result = self._values.get("instance_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#label Pipeline#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#node_type_id Pipeline#node_type_id}.'''
        result = self._values.get("node_type_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#num_workers Pipeline#num_workers}.'''
        result = self._values.get("num_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#policy_id Pipeline#policy_id}.'''
        result = self._values.get("policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_conf(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spark_conf Pipeline#spark_conf}.'''
        result = self._values.get("spark_conf")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def spark_env_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spark_env_vars Pipeline#spark_env_vars}.'''
        result = self._values.get("spark_env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ssh_public_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ssh_public_keys Pipeline#ssh_public_keys}.'''
        result = self._values.get("ssh_public_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAutoscale",
    jsii_struct_bases=[],
    name_mapping={
        "max_workers": "maxWorkers",
        "min_workers": "minWorkers",
        "mode": "mode",
    },
)
class PipelineClusterAutoscale:
    def __init__(
        self,
        *,
        max_workers: jsii.Number,
        min_workers: jsii.Number,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#max_workers Pipeline#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#min_workers Pipeline#min_workers}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#mode Pipeline#mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce9dbede4bc9a58022da5c6666000951606d7469efb5f28c295854e1e8fd39f)
            check_type(argname="argument max_workers", value=max_workers, expected_type=type_hints["max_workers"])
            check_type(argname="argument min_workers", value=min_workers, expected_type=type_hints["min_workers"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_workers": max_workers,
            "min_workers": min_workers,
        }
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def max_workers(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#max_workers Pipeline#max_workers}.'''
        result = self._values.get("max_workers")
        assert result is not None, "Required property 'max_workers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_workers(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#min_workers Pipeline#min_workers}.'''
        result = self._values.get("min_workers")
        assert result is not None, "Required property 'min_workers' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#mode Pipeline#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterAutoscale(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterAutoscaleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAutoscaleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fe15f6c1a9249712f05e440ce11e0b30acac9602246d78f80ba0758db838184)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property
    @jsii.member(jsii_name="maxWorkersInput")
    def max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="minWorkersInput")
    def min_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkers")
    def max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkers"))

    @max_workers.setter
    def max_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1de2e1df5ff136f8a6f63727b1d9c1fb15458f0b18f73b66b7110113b77c6f34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minWorkers")
    def min_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minWorkers"))

    @min_workers.setter
    def min_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee74f8f8c5c1d7fd5f4b9519da168cd76d4c3f3d3e46252648b51cfd42b1b0b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2490e45c321bce5143fc9469797d25aad3f55427c63792136e67ba3841f1b72d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterAutoscale]:
        return typing.cast(typing.Optional[PipelineClusterAutoscale], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineClusterAutoscale]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f6a54e5864a25d6af8b60f500df02f15b14660f82002791aac4b6c303729f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAwsAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "ebs_volume_count": "ebsVolumeCount",
        "ebs_volume_iops": "ebsVolumeIops",
        "ebs_volume_size": "ebsVolumeSize",
        "ebs_volume_throughput": "ebsVolumeThroughput",
        "ebs_volume_type": "ebsVolumeType",
        "first_on_demand": "firstOnDemand",
        "instance_profile_arn": "instanceProfileArn",
        "spot_bid_price_percent": "spotBidPricePercent",
        "zone_id": "zoneId",
    },
)
class PipelineClusterAwsAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_count Pipeline#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_iops Pipeline#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_size Pipeline#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_throughput Pipeline#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_type Pipeline#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#instance_profile_arn Pipeline#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_price_percent Pipeline#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7af026888b5f18b35e61519c1f99736e7f97b6cb88e4e5da33bff53a960954b8)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument ebs_volume_count", value=ebs_volume_count, expected_type=type_hints["ebs_volume_count"])
            check_type(argname="argument ebs_volume_iops", value=ebs_volume_iops, expected_type=type_hints["ebs_volume_iops"])
            check_type(argname="argument ebs_volume_size", value=ebs_volume_size, expected_type=type_hints["ebs_volume_size"])
            check_type(argname="argument ebs_volume_throughput", value=ebs_volume_throughput, expected_type=type_hints["ebs_volume_throughput"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument spot_bid_price_percent", value=spot_bid_price_percent, expected_type=type_hints["spot_bid_price_percent"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if ebs_volume_count is not None:
            self._values["ebs_volume_count"] = ebs_volume_count
        if ebs_volume_iops is not None:
            self._values["ebs_volume_iops"] = ebs_volume_iops
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if ebs_volume_throughput is not None:
            self._values["ebs_volume_throughput"] = ebs_volume_throughput
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if spot_bid_price_percent is not None:
            self._values["spot_bid_price_percent"] = spot_bid_price_percent
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_volume_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_count Pipeline#ebs_volume_count}.'''
        result = self._values.get("ebs_volume_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_iops Pipeline#ebs_volume_iops}.'''
        result = self._values.get("ebs_volume_iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_size Pipeline#ebs_volume_size}.'''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_throughput Pipeline#ebs_volume_throughput}.'''
        result = self._values.get("ebs_volume_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_type Pipeline#ebs_volume_type}.'''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#instance_profile_arn Pipeline#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_bid_price_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_price_percent Pipeline#spot_bid_price_percent}.'''
        result = self._values.get("spot_bid_price_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterAwsAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterAwsAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAwsAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__034af8c7fa271cf66adfc33f002ac3ee09bbea29825a7a8a2647deff6dbb65cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetEbsVolumeCount")
    def reset_ebs_volume_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeCount", []))

    @jsii.member(jsii_name="resetEbsVolumeIops")
    def reset_ebs_volume_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeIops", []))

    @jsii.member(jsii_name="resetEbsVolumeSize")
    def reset_ebs_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeSize", []))

    @jsii.member(jsii_name="resetEbsVolumeThroughput")
    def reset_ebs_volume_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeThroughput", []))

    @jsii.member(jsii_name="resetEbsVolumeType")
    def reset_ebs_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeType", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetSpotBidPricePercent")
    def reset_spot_bid_price_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidPricePercent", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeCountInput")
    def ebs_volume_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeCountInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIopsInput")
    def ebs_volume_iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeIopsInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSizeInput")
    def ebs_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughputInput")
    def ebs_volume_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeThroughputInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeTypeInput")
    def ebs_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ebsVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercentInput")
    def spot_bid_price_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotBidPricePercentInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="availability")
    def availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availability"))

    @availability.setter
    def availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b50743b0d980404218c560ac09acfaffed33d1c6ccd6ad9da71214f7bc9d908)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeCount")
    def ebs_volume_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeCount"))

    @ebs_volume_count.setter
    def ebs_volume_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37387d1544fb8e3dbf449aebbaa72791266b980f0562f25f5b05006f984ec526)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeIops")
    def ebs_volume_iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeIops"))

    @ebs_volume_iops.setter
    def ebs_volume_iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aedfb19135ad615868146bf69fba2d2d0910c26664440948c47548851bfdd5f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeIops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeSize")
    def ebs_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeSize"))

    @ebs_volume_size.setter
    def ebs_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dae3879597c52418887e3550f959a7acb3bc5c668705591b1eaa3eee00e4277e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeThroughput")
    def ebs_volume_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeThroughput"))

    @ebs_volume_throughput.setter
    def ebs_volume_throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a48c57fd175b08a2aeb463136fab3c209164b185d54afdf43c27758c3c37502)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeThroughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsVolumeType")
    def ebs_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ebsVolumeType"))

    @ebs_volume_type.setter
    def ebs_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b40173b02b1a8c511dcfbc4fa2513d972ea31a77a5e6eb4c2cb90c05dda9a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e32f3a85628d46feaeb90af7b67ee0b258dd99c2fcab6cd79bed11f0b4b938f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__277411d5e8b44aa476e27b98f9c3930880135294b36118d3e1416d3b4e9681d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidPricePercent")
    def spot_bid_price_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidPricePercent"))

    @spot_bid_price_percent.setter
    def spot_bid_price_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51a35bc8b068430d974cbdf4d55b6a7861e4bef5c158f0970c23240a16453a72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidPricePercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9bab925d3a74619b9a4b087b1f7809fc08d20aad58cb31ed7281b64fb6bd6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterAwsAttributes]:
        return typing.cast(typing.Optional[PipelineClusterAwsAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterAwsAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67052b274b614fdd8ff2840e90fd0d7a48e9a5f9470d24c72a7b1fd4f96631c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAzureAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "first_on_demand": "firstOnDemand",
        "log_analytics_info": "logAnalyticsInfo",
        "spot_bid_max_price": "spotBidMaxPrice",
    },
)
class PipelineClusterAzureAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union["PipelineClusterAzureAttributesLogAnalyticsInfo", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_info Pipeline#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_max_price Pipeline#spot_bid_max_price}.
        '''
        if isinstance(log_analytics_info, dict):
            log_analytics_info = PipelineClusterAzureAttributesLogAnalyticsInfo(**log_analytics_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09db73fe322631947c9826880885b081d3e940872effb957617546e6ee0a0d46)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument log_analytics_info", value=log_analytics_info, expected_type=type_hints["log_analytics_info"])
            check_type(argname="argument spot_bid_max_price", value=spot_bid_max_price, expected_type=type_hints["spot_bid_max_price"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if log_analytics_info is not None:
            self._values["log_analytics_info"] = log_analytics_info
        if spot_bid_max_price is not None:
            self._values["spot_bid_max_price"] = spot_bid_max_price

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_analytics_info(
        self,
    ) -> typing.Optional["PipelineClusterAzureAttributesLogAnalyticsInfo"]:
        '''log_analytics_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_info Pipeline#log_analytics_info}
        '''
        result = self._values.get("log_analytics_info")
        return typing.cast(typing.Optional["PipelineClusterAzureAttributesLogAnalyticsInfo"], result)

    @builtins.property
    def spot_bid_max_price(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_max_price Pipeline#spot_bid_max_price}.'''
        result = self._values.get("spot_bid_max_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterAzureAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAzureAttributesLogAnalyticsInfo",
    jsii_struct_bases=[],
    name_mapping={
        "log_analytics_primary_key": "logAnalyticsPrimaryKey",
        "log_analytics_workspace_id": "logAnalyticsWorkspaceId",
    },
)
class PipelineClusterAzureAttributesLogAnalyticsInfo:
    def __init__(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_primary_key Pipeline#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_workspace_id Pipeline#log_analytics_workspace_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afefa7827dfb374f9f885354a0b343abf0cc7cead55481375fbfa8cd08318b92)
            check_type(argname="argument log_analytics_primary_key", value=log_analytics_primary_key, expected_type=type_hints["log_analytics_primary_key"])
            check_type(argname="argument log_analytics_workspace_id", value=log_analytics_workspace_id, expected_type=type_hints["log_analytics_workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_analytics_primary_key is not None:
            self._values["log_analytics_primary_key"] = log_analytics_primary_key
        if log_analytics_workspace_id is not None:
            self._values["log_analytics_workspace_id"] = log_analytics_workspace_id

    @builtins.property
    def log_analytics_primary_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_primary_key Pipeline#log_analytics_primary_key}.'''
        result = self._values.get("log_analytics_primary_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_analytics_workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_workspace_id Pipeline#log_analytics_workspace_id}.'''
        result = self._values.get("log_analytics_workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterAzureAttributesLogAnalyticsInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterAzureAttributesLogAnalyticsInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAzureAttributesLogAnalyticsInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa16f341bb160d1bbb48d01a8357201c95db864e1b194b8871dc809460f784e2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLogAnalyticsPrimaryKey")
    def reset_log_analytics_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsPrimaryKey", []))

    @jsii.member(jsii_name="resetLogAnalyticsWorkspaceId")
    def reset_log_analytics_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsWorkspaceId", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKeyInput")
    def log_analytics_primary_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsPrimaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceIdInput")
    def log_analytics_workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logAnalyticsWorkspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsPrimaryKey")
    def log_analytics_primary_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsPrimaryKey"))

    @log_analytics_primary_key.setter
    def log_analytics_primary_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d9087909d34e3c2226d0972f4cd76b90fa0a04da8dbb8ce825070c727d48e5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsPrimaryKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsWorkspaceId")
    def log_analytics_workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logAnalyticsWorkspaceId"))

    @log_analytics_workspace_id.setter
    def log_analytics_workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef71a8a50b41cfd85b233c56bd8c93bc1972d5fbbdbae55e82bfea741f4c5faa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAnalyticsWorkspaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bd522fade832d0bb384e8757a6a40ee442ac74771d3bd211e4f42a57d89c6e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterAzureAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterAzureAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__51364aa45ea420fb8b9c47d02ef8d6aea243db86d51ad38d128bcfc4d46ec26d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLogAnalyticsInfo")
    def put_log_analytics_info(
        self,
        *,
        log_analytics_primary_key: typing.Optional[builtins.str] = None,
        log_analytics_workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param log_analytics_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_primary_key Pipeline#log_analytics_primary_key}.
        :param log_analytics_workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_workspace_id Pipeline#log_analytics_workspace_id}.
        '''
        value = PipelineClusterAzureAttributesLogAnalyticsInfo(
            log_analytics_primary_key=log_analytics_primary_key,
            log_analytics_workspace_id=log_analytics_workspace_id,
        )

        return typing.cast(None, jsii.invoke(self, "putLogAnalyticsInfo", [value]))

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetLogAnalyticsInfo")
    def reset_log_analytics_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAnalyticsInfo", []))

    @jsii.member(jsii_name="resetSpotBidMaxPrice")
    def reset_spot_bid_max_price(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotBidMaxPrice", []))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfo")
    def log_analytics_info(
        self,
    ) -> PipelineClusterAzureAttributesLogAnalyticsInfoOutputReference:
        return typing.cast(PipelineClusterAzureAttributesLogAnalyticsInfoOutputReference, jsii.get(self, "logAnalyticsInfo"))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="logAnalyticsInfoInput")
    def log_analytics_info_input(
        self,
    ) -> typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo]:
        return typing.cast(typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo], jsii.get(self, "logAnalyticsInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPriceInput")
    def spot_bid_max_price_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotBidMaxPriceInput"))

    @builtins.property
    @jsii.member(jsii_name="availability")
    def availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availability"))

    @availability.setter
    def availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6deaf78af2052e90547146e612e964cbf9d69f3f06e2138233a63c69365fd643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77b9cb2951bd82daa4adf7365a6017d47d9a8eaab7a7543741c41374cb91e86f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotBidMaxPrice")
    def spot_bid_max_price(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotBidMaxPrice"))

    @spot_bid_max_price.setter
    def spot_bid_max_price(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dffe0a39f86ee95c49dd36e8c2f362709827f1996521fa8af5a82fb475c9d23c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotBidMaxPrice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterAzureAttributes]:
        return typing.cast(typing.Optional[PipelineClusterAzureAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterAzureAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3281128a46c79bcb7d3db67dc3d6665e954f411e21cbc4bdbe0c6ba486d2fe1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConf",
    jsii_struct_bases=[],
    name_mapping={"dbfs": "dbfs", "s3": "s3", "volumes": "volumes"},
)
class PipelineClusterClusterLogConf:
    def __init__(
        self,
        *,
        dbfs: typing.Optional[typing.Union["PipelineClusterClusterLogConfDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["PipelineClusterClusterLogConfS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["PipelineClusterClusterLogConfVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dbfs Pipeline#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#s3 Pipeline#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#volumes Pipeline#volumes}
        '''
        if isinstance(dbfs, dict):
            dbfs = PipelineClusterClusterLogConfDbfs(**dbfs)
        if isinstance(s3, dict):
            s3 = PipelineClusterClusterLogConfS3(**s3)
        if isinstance(volumes, dict):
            volumes = PipelineClusterClusterLogConfVolumes(**volumes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdae64159d2d4575c3ac781cbce96f2254c0e060d4424a3ccb2b7fc8517509ae)
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def dbfs(self) -> typing.Optional["PipelineClusterClusterLogConfDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dbfs Pipeline#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["PipelineClusterClusterLogConfDbfs"], result)

    @builtins.property
    def s3(self) -> typing.Optional["PipelineClusterClusterLogConfS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#s3 Pipeline#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["PipelineClusterClusterLogConfS3"], result)

    @builtins.property
    def volumes(self) -> typing.Optional["PipelineClusterClusterLogConfVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#volumes Pipeline#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["PipelineClusterClusterLogConfVolumes"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterClusterLogConf(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterClusterLogConfDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79c754560b803a4ed489c688433906f7b8250a6e1f2694e35934e024fa375f07)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterClusterLogConfDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterClusterLogConfDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dfc342752bd16830b28a56b50b1bb61f39209662af4c6d1e91ad5adbfaf2c4d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b53c6c3f82ebf7e3fbe7d31a6dccb41352abca30fc763ed1e1a2a7c19363e262)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterClusterLogConfDbfs]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConfDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterClusterLogConfDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fc9f865a104a1f27a96d3d66e17cc8a72925c203a7cc009ea0d8698f1dcece6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterClusterLogConfOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fad27a78ca71664a0e32853ca8b6b3a51eceb93dd4dce71303cbd3b246a8e4ea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterClusterLogConfDbfs(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.
        '''
        value = PipelineClusterClusterLogConfS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterClusterLogConfVolumes(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(self) -> PipelineClusterClusterLogConfDbfsOutputReference:
        return typing.cast(PipelineClusterClusterLogConfDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(self) -> "PipelineClusterClusterLogConfS3OutputReference":
        return typing.cast("PipelineClusterClusterLogConfS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> "PipelineClusterClusterLogConfVolumesOutputReference":
        return typing.cast("PipelineClusterClusterLogConfVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(self) -> typing.Optional[PipelineClusterClusterLogConfDbfs]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConfDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["PipelineClusterClusterLogConfS3"]:
        return typing.cast(typing.Optional["PipelineClusterClusterLogConfS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(self) -> typing.Optional["PipelineClusterClusterLogConfVolumes"]:
        return typing.cast(typing.Optional["PipelineClusterClusterLogConfVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterClusterLogConf]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConf], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterClusterLogConf],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e6d68c3bc3a9e8d7c64137a82f6463564fe8d3791b8cafac3b26f9bd953a6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class PipelineClusterClusterLogConfS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fec978197dc868cbe45df928a2d5427576192a929c3b00a61f7e5edc7af2d44)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterClusterLogConfS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterClusterLogConfS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc7cb8fe5a0fd58e17ae409bf69c4646d59dda0df1d864ad7a72fd90c517adae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a31d1241d7f8f609a6ef5a382f16522098525df752b68cf1868e4ddbd75241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63a09afb8148ba93a8e2c12adf938bd1dfa4cac1c2da2d66fbde7d9b5bcf72af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e07070e38bf0266faa6c18548919fc882c6e4d5fa1df021c6b73fb5e377c119)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc46bd2b8f68fcaa82a11a2e05523f59b6345b4c5fec20c9c7a49d0e559384f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aeabb05479bc828373b47bdea1405e6a69e6a724b04e8ba93232bad5ca963fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__683832da4aba9347cb5750987bb4ef264764efb3d01620167644c18ea591b74b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__695465dc2be754fbd2e05a184c8487266b265af299ca7b6b13327cf4caf1ff93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterClusterLogConfS3]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConfS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterClusterLogConfS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f58f1cdd11eae849fb94989e6b66c7e7a4cebceff8c52d310318bb10f4736679)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterClusterLogConfVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__042fb7e8d8e1065b150883eaf40acbc92e36a6ca366a8d658b03d45d7b44a99b)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterClusterLogConfVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterClusterLogConfVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterClusterLogConfVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8ddbb72fff1a48b044e3b0b05d5ec0a3965e6caf472691f3cce6675143290e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a86987bdb43a8311ed9e512f4c8d5e0a219d17045dce1535fd443ad2d6f5fa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterClusterLogConfVolumes]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConfVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterClusterLogConfVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9645be08c560333683e2e7b35a7d635c5692ddb9cbe074f8333a4492fa975a36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterGcpAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "first_on_demand": "firstOnDemand",
        "google_service_account": "googleServiceAccount",
        "local_ssd_count": "localSsdCount",
        "zone_id": "zoneId",
    },
)
class PipelineClusterGcpAttributes:
    def __init__(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#google_service_account Pipeline#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#local_ssd_count Pipeline#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b710373a181627bd2598489140676a7d69d36adfe98c520af7e0e3d394c3f0f5)
            check_type(argname="argument availability", value=availability, expected_type=type_hints["availability"])
            check_type(argname="argument first_on_demand", value=first_on_demand, expected_type=type_hints["first_on_demand"])
            check_type(argname="argument google_service_account", value=google_service_account, expected_type=type_hints["google_service_account"])
            check_type(argname="argument local_ssd_count", value=local_ssd_count, expected_type=type_hints["local_ssd_count"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability is not None:
            self._values["availability"] = availability
        if first_on_demand is not None:
            self._values["first_on_demand"] = first_on_demand
        if google_service_account is not None:
            self._values["google_service_account"] = google_service_account
        if local_ssd_count is not None:
            self._values["local_ssd_count"] = local_ssd_count
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def availability(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.'''
        result = self._values.get("availability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_on_demand(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.'''
        result = self._values.get("first_on_demand")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def google_service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#google_service_account Pipeline#google_service_account}.'''
        result = self._values.get("google_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#local_ssd_count Pipeline#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterGcpAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterGcpAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterGcpAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__592209e8eed1f04fcad13ceba385289a14b46ea300f3529d3fe46916c2e3336a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailability")
    def reset_availability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailability", []))

    @jsii.member(jsii_name="resetFirstOnDemand")
    def reset_first_on_demand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirstOnDemand", []))

    @jsii.member(jsii_name="resetGoogleServiceAccount")
    def reset_google_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleServiceAccount", []))

    @jsii.member(jsii_name="resetLocalSsdCount")
    def reset_local_ssd_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSsdCount", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityInput")
    def availability_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="firstOnDemandInput")
    def first_on_demand_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "firstOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccountInput")
    def google_service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "googleServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="localSsdCountInput")
    def local_ssd_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localSsdCountInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="availability")
    def availability(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availability"))

    @availability.setter
    def availability(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccfb66e1048f88ad8ae8b81fb2cc1030de5f2dc3ffde38da0ef080caf2358bea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availability", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstOnDemand")
    def first_on_demand(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "firstOnDemand"))

    @first_on_demand.setter
    def first_on_demand(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c2dd36ea6ca4657d2b814a407283fac06f027f13850cee388c221033c0c7f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleServiceAccount")
    def google_service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "googleServiceAccount"))

    @google_service_account.setter
    def google_service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc6db22f54dbae2c8bfa0e6de14dc2f6636312e44f4bc7d2f9d2f42962b56570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleServiceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d6221c0bc0eadb022d9386f12e2ad44cc8a87677616c4bc1300b406f6413d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3ae1f293d1c69e590a0befd3409e1af4349116c4e9949edaf56a4f7dde5af9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterGcpAttributes]:
        return typing.cast(typing.Optional[PipelineClusterGcpAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterGcpAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__426feba19e4b7f80d3d89b2ef788d55e1b23568cc54c9aeacbf28ff62b855dad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScripts",
    jsii_struct_bases=[],
    name_mapping={
        "abfss": "abfss",
        "dbfs": "dbfs",
        "file": "file",
        "gcs": "gcs",
        "s3": "s3",
        "volumes": "volumes",
        "workspace": "workspace",
    },
)
class PipelineClusterInitScripts:
    def __init__(
        self,
        *,
        abfss: typing.Optional[typing.Union["PipelineClusterInitScriptsAbfss", typing.Dict[builtins.str, typing.Any]]] = None,
        dbfs: typing.Optional[typing.Union["PipelineClusterInitScriptsDbfs", typing.Dict[builtins.str, typing.Any]]] = None,
        file: typing.Optional[typing.Union["PipelineClusterInitScriptsFile", typing.Dict[builtins.str, typing.Any]]] = None,
        gcs: typing.Optional[typing.Union["PipelineClusterInitScriptsGcs", typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["PipelineClusterInitScriptsS3", typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union["PipelineClusterInitScriptsVolumes", typing.Dict[builtins.str, typing.Any]]] = None,
        workspace: typing.Optional[typing.Union["PipelineClusterInitScriptsWorkspace", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param abfss: abfss block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#abfss Pipeline#abfss}
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dbfs Pipeline#dbfs}
        :param file: file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#file Pipeline#file}
        :param gcs: gcs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gcs Pipeline#gcs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#s3 Pipeline#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#volumes Pipeline#volumes}
        :param workspace: workspace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#workspace Pipeline#workspace}
        '''
        if isinstance(abfss, dict):
            abfss = PipelineClusterInitScriptsAbfss(**abfss)
        if isinstance(dbfs, dict):
            dbfs = PipelineClusterInitScriptsDbfs(**dbfs)
        if isinstance(file, dict):
            file = PipelineClusterInitScriptsFile(**file)
        if isinstance(gcs, dict):
            gcs = PipelineClusterInitScriptsGcs(**gcs)
        if isinstance(s3, dict):
            s3 = PipelineClusterInitScriptsS3(**s3)
        if isinstance(volumes, dict):
            volumes = PipelineClusterInitScriptsVolumes(**volumes)
        if isinstance(workspace, dict):
            workspace = PipelineClusterInitScriptsWorkspace(**workspace)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9606725d916bb4025b10a7e8de1a9bb8400329fca569201ea64471d72b11ca82)
            check_type(argname="argument abfss", value=abfss, expected_type=type_hints["abfss"])
            check_type(argname="argument dbfs", value=dbfs, expected_type=type_hints["dbfs"])
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument gcs", value=gcs, expected_type=type_hints["gcs"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
            check_type(argname="argument workspace", value=workspace, expected_type=type_hints["workspace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if abfss is not None:
            self._values["abfss"] = abfss
        if dbfs is not None:
            self._values["dbfs"] = dbfs
        if file is not None:
            self._values["file"] = file
        if gcs is not None:
            self._values["gcs"] = gcs
        if s3 is not None:
            self._values["s3"] = s3
        if volumes is not None:
            self._values["volumes"] = volumes
        if workspace is not None:
            self._values["workspace"] = workspace

    @builtins.property
    def abfss(self) -> typing.Optional["PipelineClusterInitScriptsAbfss"]:
        '''abfss block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#abfss Pipeline#abfss}
        '''
        result = self._values.get("abfss")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsAbfss"], result)

    @builtins.property
    def dbfs(self) -> typing.Optional["PipelineClusterInitScriptsDbfs"]:
        '''dbfs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dbfs Pipeline#dbfs}
        '''
        result = self._values.get("dbfs")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsDbfs"], result)

    @builtins.property
    def file(self) -> typing.Optional["PipelineClusterInitScriptsFile"]:
        '''file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#file Pipeline#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsFile"], result)

    @builtins.property
    def gcs(self) -> typing.Optional["PipelineClusterInitScriptsGcs"]:
        '''gcs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gcs Pipeline#gcs}
        '''
        result = self._values.get("gcs")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsGcs"], result)

    @builtins.property
    def s3(self) -> typing.Optional["PipelineClusterInitScriptsS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#s3 Pipeline#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsS3"], result)

    @builtins.property
    def volumes(self) -> typing.Optional["PipelineClusterInitScriptsVolumes"]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#volumes Pipeline#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsVolumes"], result)

    @builtins.property
    def workspace(self) -> typing.Optional["PipelineClusterInitScriptsWorkspace"]:
        '''workspace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#workspace Pipeline#workspace}
        '''
        result = self._values.get("workspace")
        return typing.cast(typing.Optional["PipelineClusterInitScriptsWorkspace"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScripts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsAbfss",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsAbfss:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e93df7a4b4e85a178aafddec8b8444061a67acc0158965c9fbc3ffdec7e08dad)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsAbfss(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsAbfssOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsAbfssOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b1a2169d341d9a1b54e145ac37e34b8b90952d5a89733fda8e2709d66f2594b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0804e0ac900175e8a31d52a0e43c9fdc97540c631bda3bac9dbbebcbac386417)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsAbfss]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsAbfss], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsAbfss],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2c7564878391e77e1ecb1813e9874fd80e410473364e40578f1cc072d990fec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsDbfs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsDbfs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773d8055d11a750f72b3f99d5f7733d209001918686e8dcc5a50db3d17f930b1)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsDbfs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsDbfsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsDbfsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a78827de0293eb00ad644174368fd942beadb0d575beb795330e3862bb3d1b95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1467dfd18b63ed1c69984b6de6b8ce9f8c3c3ab74726298318a3f058704f769f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsDbfs]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsDbfs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsDbfs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f9edcb9e850114867de2f6ee074dde5259a6471e37f4e4e584aeec2a540300)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsFile",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsFile:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6fd7dc19949d16fec90ab1a0ff7e085302b16993a48869f0937d270c22015b7)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__701886f366bcab6170c3bd2394fc427805182567a9fdfdd32c2aa09b6dc0f0f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bfea21e750306c5b21603223837912010c380ae90b7df3466b885c784955173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsFile]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsFile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsFile],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5007b948901d62e9d63d21638cde663252a03b024cb433830cc9ab209099d26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsGcs",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsGcs:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30819dbed6df23b53891b67db4dce91d1e68aebb8b25f3ab57511c55606c72a3)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsGcs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsGcsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsGcsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d21302844a476d5838e4e296a138354123b06c50d1cb6b0e70d524e468abce93)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__949518cb359e176b60a494e19d76e6396a08020e77808e52f993443f1e6a132c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsGcs]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsGcs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsGcs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8330567bbc43ad983641908cf4a97440f3d16d09c224be7c9ecfbd5658a9b9f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterInitScriptsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__879fac48a3d2b2371b4586c591c212b08ab4682f869eabc73441135e7b32d798)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PipelineClusterInitScriptsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1809a156de53f72403132d5a340b04299149cba61a7e75a73765f6fb36d36505)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineClusterInitScriptsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6f49650ee13adfbdb2d603e541f611196b928ecdb2be39caa61326c592ae123)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6abd859892e7b5393262d0559d4bb68a54b9473912df0611d2077219bf7850a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02229def7288e4c942fa5346afafdc85ac80f9dd7ee03198e919889e4ce2d231)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d62682f2e79cf083bbc5824c1155d3e621e4003798cf73e1c3229a20e12fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterInitScriptsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a844dab2df04ef50ff41322260f02051dca754ee9dd06dba4792fdde06f92f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAbfss")
    def put_abfss(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsAbfss(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putAbfss", [value]))

    @jsii.member(jsii_name="putDbfs")
    def put_dbfs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsDbfs(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putDbfs", [value]))

    @jsii.member(jsii_name="putFile")
    def put_file(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsFile(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putFile", [value]))

    @jsii.member(jsii_name="putGcs")
    def put_gcs(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsGcs(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putGcs", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.
        '''
        value = PipelineClusterInitScriptsS3(
            destination=destination,
            canned_acl=canned_acl,
            enable_encryption=enable_encryption,
            encryption_type=encryption_type,
            endpoint=endpoint,
            kms_key=kms_key,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putVolumes")
    def put_volumes(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsVolumes(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putVolumes", [value]))

    @jsii.member(jsii_name="putWorkspace")
    def put_workspace(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        value = PipelineClusterInitScriptsWorkspace(destination=destination)

        return typing.cast(None, jsii.invoke(self, "putWorkspace", [value]))

    @jsii.member(jsii_name="resetAbfss")
    def reset_abfss(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAbfss", []))

    @jsii.member(jsii_name="resetDbfs")
    def reset_dbfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbfs", []))

    @jsii.member(jsii_name="resetFile")
    def reset_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFile", []))

    @jsii.member(jsii_name="resetGcs")
    def reset_gcs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcs", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @jsii.member(jsii_name="resetWorkspace")
    def reset_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspace", []))

    @builtins.property
    @jsii.member(jsii_name="abfss")
    def abfss(self) -> PipelineClusterInitScriptsAbfssOutputReference:
        return typing.cast(PipelineClusterInitScriptsAbfssOutputReference, jsii.get(self, "abfss"))

    @builtins.property
    @jsii.member(jsii_name="dbfs")
    def dbfs(self) -> PipelineClusterInitScriptsDbfsOutputReference:
        return typing.cast(PipelineClusterInitScriptsDbfsOutputReference, jsii.get(self, "dbfs"))

    @builtins.property
    @jsii.member(jsii_name="file")
    def file(self) -> PipelineClusterInitScriptsFileOutputReference:
        return typing.cast(PipelineClusterInitScriptsFileOutputReference, jsii.get(self, "file"))

    @builtins.property
    @jsii.member(jsii_name="gcs")
    def gcs(self) -> PipelineClusterInitScriptsGcsOutputReference:
        return typing.cast(PipelineClusterInitScriptsGcsOutputReference, jsii.get(self, "gcs"))

    @builtins.property
    @jsii.member(jsii_name="s3")
    def s3(self) -> "PipelineClusterInitScriptsS3OutputReference":
        return typing.cast("PipelineClusterInitScriptsS3OutputReference", jsii.get(self, "s3"))

    @builtins.property
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> "PipelineClusterInitScriptsVolumesOutputReference":
        return typing.cast("PipelineClusterInitScriptsVolumesOutputReference", jsii.get(self, "volumes"))

    @builtins.property
    @jsii.member(jsii_name="workspace")
    def workspace(self) -> "PipelineClusterInitScriptsWorkspaceOutputReference":
        return typing.cast("PipelineClusterInitScriptsWorkspaceOutputReference", jsii.get(self, "workspace"))

    @builtins.property
    @jsii.member(jsii_name="abfssInput")
    def abfss_input(self) -> typing.Optional[PipelineClusterInitScriptsAbfss]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsAbfss], jsii.get(self, "abfssInput"))

    @builtins.property
    @jsii.member(jsii_name="dbfsInput")
    def dbfs_input(self) -> typing.Optional[PipelineClusterInitScriptsDbfs]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsDbfs], jsii.get(self, "dbfsInput"))

    @builtins.property
    @jsii.member(jsii_name="fileInput")
    def file_input(self) -> typing.Optional[PipelineClusterInitScriptsFile]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsFile], jsii.get(self, "fileInput"))

    @builtins.property
    @jsii.member(jsii_name="gcsInput")
    def gcs_input(self) -> typing.Optional[PipelineClusterInitScriptsGcs]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsGcs], jsii.get(self, "gcsInput"))

    @builtins.property
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["PipelineClusterInitScriptsS3"]:
        return typing.cast(typing.Optional["PipelineClusterInitScriptsS3"], jsii.get(self, "s3Input"))

    @builtins.property
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(self) -> typing.Optional["PipelineClusterInitScriptsVolumes"]:
        return typing.cast(typing.Optional["PipelineClusterInitScriptsVolumes"], jsii.get(self, "volumesInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceInput")
    def workspace_input(self) -> typing.Optional["PipelineClusterInitScriptsWorkspace"]:
        return typing.cast(typing.Optional["PipelineClusterInitScriptsWorkspace"], jsii.get(self, "workspaceInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineClusterInitScripts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineClusterInitScripts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineClusterInitScripts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27ac8fca519ed0fcea396a2ec6613ec1ba834ef4cd46a535468c6386ba4a8bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsS3",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "canned_acl": "cannedAcl",
        "enable_encryption": "enableEncryption",
        "encryption_type": "encryptionType",
        "endpoint": "endpoint",
        "kms_key": "kmsKey",
        "region": "region",
    },
)
class PipelineClusterInitScriptsS3:
    def __init__(
        self,
        *,
        destination: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
        enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_type: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        :param canned_acl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.
        :param enable_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.
        :param encryption_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.
        :param endpoint: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.
        :param kms_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2045e73bbb4999b3222f9ed41e0b08c4ec5686ca7807cf426616d71db8ae44f8)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument canned_acl", value=canned_acl, expected_type=type_hints["canned_acl"])
            check_type(argname="argument enable_encryption", value=enable_encryption, expected_type=type_hints["enable_encryption"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl
        if enable_encryption is not None:
            self._values["enable_encryption"] = enable_encryption
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#canned_acl Pipeline#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#enable_encryption Pipeline#enable_encryption}.'''
        result = self._values.get("enable_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#encryption_type Pipeline#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#endpoint Pipeline#endpoint}.'''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kms_key Pipeline#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#region Pipeline#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsS3OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsS3OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8db4af9da6a51f8e4ffbc84afda9627a9ec02930ef26256f67e1f8bb8b0014ba)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @jsii.member(jsii_name="resetEnableEncryption")
    def reset_enable_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableEncryption", []))

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="enableEncryptionInput")
    def enable_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45de8c1834d4b16a41b09c1548a9c9ce0fe7be5ead905653869a0d10aa972c15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cannedAcl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dc9f8cedd2d53468f49658fd2487abe0b5fb9cdd2aab571474bb6accc5b4871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableEncryption")
    def enable_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableEncryption"))

    @enable_encryption.setter
    def enable_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a7a77c34aada88dc679f75ed0a0297fb6a482b369330560d8684481ff92621d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__843e85deae8b66607c2486c93edd7c99b48fcf401748b3598b427b27de555f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0faa7a03216b2933a7fb25039c083b71bfa404c8e4e44aee1d820b6c89d608f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6306b195cbf041ad83e6e5c1a42e0f6828eeed3d597954793422883419a7eaad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__139e883bc023de2afca0288b96704b37662fc11767b1613f8388ad54812572f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsS3]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsS3],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6547b1abae046c7250fd7f2e0891d476789b6eee05d869243b1811198525b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsVolumes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsVolumes:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e2ac50bd3ed45f5790abb81df5757f39746eb8588abb487c931408ef401f3b)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsVolumesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsVolumesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6429efd050eca9fe8e4e24287719a27cb795f2cdc1c24feeff42a0db386792e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7413a0a395a01837c5fc91f95da0310683f07665a3a508a3358a9b543191e9ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsVolumes]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsVolumes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsVolumes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ec2f7ef6eb7e69a434441eaaf8a372464617aecf972ec865d01ef6cc784b04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsWorkspace",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination"},
)
class PipelineClusterInitScriptsWorkspace:
    def __init__(self, *, destination: builtins.str) -> None:
        '''
        :param destination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3075f0ce66fa7869601bb651bec348c898120755aed86f2b322985c6508a76e0)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }

    @builtins.property
    def destination(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination Pipeline#destination}.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineClusterInitScriptsWorkspace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineClusterInitScriptsWorkspaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterInitScriptsWorkspaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2860bf0abc4996f8888cab5b15660198fd769fc8a24047706a48bf064182db0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destination"))

    @destination.setter
    def destination(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd89e07da7d3805379507e8700987ace948bf9e0882cb3241a935ae10f8caf15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineClusterInitScriptsWorkspace]:
        return typing.cast(typing.Optional[PipelineClusterInitScriptsWorkspace], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineClusterInitScriptsWorkspace],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c333e2ea596dd4ce3be82fabccf3c7186aa2444c106dc8ccad66b50cb32b88ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b6853e27ebc950e9ebfbdc65a2671e90f8ee99067592d8c545a59e96206f64b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PipelineClusterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__996df806c4a3a7163cea3aaef61a4d888356d399d5b03946300dfcd829841055)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineClusterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b33a40ebfcfb0a454d6b6df420e22a3487fe6662e19511f0f38f0aa57e87337)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0906c1235da71a2dc07c438f07c59ad86868ac130b0d90832afd037c529fb320)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c725476ac49792590c40a2ecf7a838d852aa7deab25c5125452f647f1e8a599e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aee7af843d919a00edf74f64b2360f55fe40a73abc4ad08072efc7c8d3bbb127)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineClusterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineClusterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__68f686b393542f758490bfc53c92a41e454b4a54842f9409c872e10216c9ee3e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAutoscale")
    def put_autoscale(
        self,
        *,
        max_workers: jsii.Number,
        min_workers: jsii.Number,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#max_workers Pipeline#max_workers}.
        :param min_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#min_workers Pipeline#min_workers}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#mode Pipeline#mode}.
        '''
        value = PipelineClusterAutoscale(
            max_workers=max_workers, min_workers=min_workers, mode=mode
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscale", [value]))

    @jsii.member(jsii_name="putAwsAttributes")
    def put_aws_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        ebs_volume_count: typing.Optional[jsii.Number] = None,
        ebs_volume_iops: typing.Optional[jsii.Number] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        ebs_volume_throughput: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        spot_bid_price_percent: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param ebs_volume_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_count Pipeline#ebs_volume_count}.
        :param ebs_volume_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_iops Pipeline#ebs_volume_iops}.
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_size Pipeline#ebs_volume_size}.
        :param ebs_volume_throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_throughput Pipeline#ebs_volume_throughput}.
        :param ebs_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ebs_volume_type Pipeline#ebs_volume_type}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#instance_profile_arn Pipeline#instance_profile_arn}.
        :param spot_bid_price_percent: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_price_percent Pipeline#spot_bid_price_percent}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.
        '''
        value = PipelineClusterAwsAttributes(
            availability=availability,
            ebs_volume_count=ebs_volume_count,
            ebs_volume_iops=ebs_volume_iops,
            ebs_volume_size=ebs_volume_size,
            ebs_volume_throughput=ebs_volume_throughput,
            ebs_volume_type=ebs_volume_type,
            first_on_demand=first_on_demand,
            instance_profile_arn=instance_profile_arn,
            spot_bid_price_percent=spot_bid_price_percent,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAwsAttributes", [value]))

    @jsii.member(jsii_name="putAzureAttributes")
    def put_azure_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        log_analytics_info: typing.Optional[typing.Union[PipelineClusterAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        spot_bid_max_price: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param log_analytics_info: log_analytics_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#log_analytics_info Pipeline#log_analytics_info}
        :param spot_bid_max_price: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#spot_bid_max_price Pipeline#spot_bid_max_price}.
        '''
        value = PipelineClusterAzureAttributes(
            availability=availability,
            first_on_demand=first_on_demand,
            log_analytics_info=log_analytics_info,
            spot_bid_max_price=spot_bid_max_price,
        )

        return typing.cast(None, jsii.invoke(self, "putAzureAttributes", [value]))

    @jsii.member(jsii_name="putClusterLogConf")
    def put_cluster_log_conf(
        self,
        *,
        dbfs: typing.Optional[typing.Union[PipelineClusterClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union[PipelineClusterClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Union[PipelineClusterClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param dbfs: dbfs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dbfs Pipeline#dbfs}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#s3 Pipeline#s3}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#volumes Pipeline#volumes}
        '''
        value = PipelineClusterClusterLogConf(dbfs=dbfs, s3=s3, volumes=volumes)

        return typing.cast(None, jsii.invoke(self, "putClusterLogConf", [value]))

    @jsii.member(jsii_name="putGcpAttributes")
    def put_gcp_attributes(
        self,
        *,
        availability: typing.Optional[builtins.str] = None,
        first_on_demand: typing.Optional[jsii.Number] = None,
        google_service_account: typing.Optional[builtins.str] = None,
        local_ssd_count: typing.Optional[jsii.Number] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#availability Pipeline#availability}.
        :param first_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#first_on_demand Pipeline#first_on_demand}.
        :param google_service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#google_service_account Pipeline#google_service_account}.
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#local_ssd_count Pipeline#local_ssd_count}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#zone_id Pipeline#zone_id}.
        '''
        value = PipelineClusterGcpAttributes(
            availability=availability,
            first_on_demand=first_on_demand,
            google_service_account=google_service_account,
            local_ssd_count=local_ssd_count,
            zone_id=zone_id,
        )

        return typing.cast(None, jsii.invoke(self, "putGcpAttributes", [value]))

    @jsii.member(jsii_name="putInitScripts")
    def put_init_scripts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineClusterInitScripts, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ccde33b89ee7e4184a4d72ec46e68fc045fd1aa55f6309fddb669ec4e34d73d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInitScripts", [value]))

    @jsii.member(jsii_name="resetApplyPolicyDefaultValues")
    def reset_apply_policy_default_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyPolicyDefaultValues", []))

    @jsii.member(jsii_name="resetAutoscale")
    def reset_autoscale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscale", []))

    @jsii.member(jsii_name="resetAwsAttributes")
    def reset_aws_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAttributes", []))

    @jsii.member(jsii_name="resetAzureAttributes")
    def reset_azure_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAttributes", []))

    @jsii.member(jsii_name="resetClusterLogConf")
    def reset_cluster_log_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterLogConf", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetDriverInstancePoolId")
    def reset_driver_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverInstancePoolId", []))

    @jsii.member(jsii_name="resetDriverNodeTypeId")
    def reset_driver_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverNodeTypeId", []))

    @jsii.member(jsii_name="resetEnableLocalDiskEncryption")
    def reset_enable_local_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLocalDiskEncryption", []))

    @jsii.member(jsii_name="resetGcpAttributes")
    def reset_gcp_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpAttributes", []))

    @jsii.member(jsii_name="resetInitScripts")
    def reset_init_scripts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitScripts", []))

    @jsii.member(jsii_name="resetInstancePoolId")
    def reset_instance_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstancePoolId", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetNodeTypeId")
    def reset_node_type_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeTypeId", []))

    @jsii.member(jsii_name="resetNumWorkers")
    def reset_num_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumWorkers", []))

    @jsii.member(jsii_name="resetPolicyId")
    def reset_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyId", []))

    @jsii.member(jsii_name="resetSparkConf")
    def reset_spark_conf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkConf", []))

    @jsii.member(jsii_name="resetSparkEnvVars")
    def reset_spark_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSparkEnvVars", []))

    @jsii.member(jsii_name="resetSshPublicKeys")
    def reset_ssh_public_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshPublicKeys", []))

    @builtins.property
    @jsii.member(jsii_name="autoscale")
    def autoscale(self) -> PipelineClusterAutoscaleOutputReference:
        return typing.cast(PipelineClusterAutoscaleOutputReference, jsii.get(self, "autoscale"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributes")
    def aws_attributes(self) -> PipelineClusterAwsAttributesOutputReference:
        return typing.cast(PipelineClusterAwsAttributesOutputReference, jsii.get(self, "awsAttributes"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributes")
    def azure_attributes(self) -> PipelineClusterAzureAttributesOutputReference:
        return typing.cast(PipelineClusterAzureAttributesOutputReference, jsii.get(self, "azureAttributes"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConf")
    def cluster_log_conf(self) -> PipelineClusterClusterLogConfOutputReference:
        return typing.cast(PipelineClusterClusterLogConfOutputReference, jsii.get(self, "clusterLogConf"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributes")
    def gcp_attributes(self) -> PipelineClusterGcpAttributesOutputReference:
        return typing.cast(PipelineClusterGcpAttributesOutputReference, jsii.get(self, "gcpAttributes"))

    @builtins.property
    @jsii.member(jsii_name="initScripts")
    def init_scripts(self) -> PipelineClusterInitScriptsList:
        return typing.cast(PipelineClusterInitScriptsList, jsii.get(self, "initScripts"))

    @builtins.property
    @jsii.member(jsii_name="applyPolicyDefaultValuesInput")
    def apply_policy_default_values_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "applyPolicyDefaultValuesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleInput")
    def autoscale_input(self) -> typing.Optional[PipelineClusterAutoscale]:
        return typing.cast(typing.Optional[PipelineClusterAutoscale], jsii.get(self, "autoscaleInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAttributesInput")
    def aws_attributes_input(self) -> typing.Optional[PipelineClusterAwsAttributes]:
        return typing.cast(typing.Optional[PipelineClusterAwsAttributes], jsii.get(self, "awsAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAttributesInput")
    def azure_attributes_input(self) -> typing.Optional[PipelineClusterAzureAttributes]:
        return typing.cast(typing.Optional[PipelineClusterAzureAttributes], jsii.get(self, "azureAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterLogConfInput")
    def cluster_log_conf_input(self) -> typing.Optional[PipelineClusterClusterLogConf]:
        return typing.cast(typing.Optional[PipelineClusterClusterLogConf], jsii.get(self, "clusterLogConfInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolIdInput")
    def driver_instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInstancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeIdInput")
    def driver_node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverNodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryptionInput")
    def enable_local_disk_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableLocalDiskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpAttributesInput")
    def gcp_attributes_input(self) -> typing.Optional[PipelineClusterGcpAttributes]:
        return typing.cast(typing.Optional[PipelineClusterGcpAttributes], jsii.get(self, "gcpAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="initScriptsInput")
    def init_scripts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]], jsii.get(self, "initScriptsInput"))

    @builtins.property
    @jsii.member(jsii_name="instancePoolIdInput")
    def instance_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instancePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeTypeIdInput")
    def node_type_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="numWorkersInput")
    def num_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkConfInput")
    def spark_conf_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkConfInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVarsInput")
    def spark_env_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sparkEnvVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeysInput")
    def ssh_public_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshPublicKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="applyPolicyDefaultValues")
    def apply_policy_default_values(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "applyPolicyDefaultValues"))

    @apply_policy_default_values.setter
    def apply_policy_default_values(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__631830709b6db135caab7afb66fa8cfa512a3adb3002d6b2885a866c05aaf90e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applyPolicyDefaultValues", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__807b1063c49427b28ed2a87a22209ee99f388bd621f8725f74ee66501892a570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverInstancePoolId")
    def driver_instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverInstancePoolId"))

    @driver_instance_pool_id.setter
    def driver_instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec550f62fe53d73b084a3dac8d01b1c4704347f726d8525bfa7103ac6046c17d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverInstancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="driverNodeTypeId")
    def driver_node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverNodeTypeId"))

    @driver_node_type_id.setter
    def driver_node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e3bb153e66bb090fc1c785e03e5d4406a79f703343bbcd503a7d7f1dfc3064)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "driverNodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableLocalDiskEncryption")
    def enable_local_disk_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableLocalDiskEncryption"))

    @enable_local_disk_encryption.setter
    def enable_local_disk_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5214bd08eeb09f4bf7f9ace89a5fd920379dfad9efdd8a8fb02f43a36bdba08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableLocalDiskEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancePoolId")
    def instance_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instancePoolId"))

    @instance_pool_id.setter
    def instance_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bfbf599ab5a89b240ba478d5b474bdd9d639d94bfc1abecf633f8ab0a5e25b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52daa4d5938a16e79cc53deec1d3e87502543fbaa68a03ca7b56b682841cbf12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeTypeId")
    def node_type_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeTypeId"))

    @node_type_id.setter
    def node_type_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9c10516fe628ee18399e140f2142998675c7303a3628e4bc2b6c7a699d06fe2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeTypeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numWorkers")
    def num_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numWorkers"))

    @num_workers.setter
    def num_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27e3cb5b1eea5fcb04ad12e214ddc57eeaf315bdbf01c057b730a5807f544a62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc63ce4e08ad091fd56b6522e12937aa41cb6e21e2dbd4625562209d77957e5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkConf")
    def spark_conf(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkConf"))

    @spark_conf.setter
    def spark_conf(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36ebca77bd76b747421301a8aafb76338163ff991bb705fc9d0f299acdd86880)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkConf", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sparkEnvVars")
    def spark_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sparkEnvVars"))

    @spark_env_vars.setter
    def spark_env_vars(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41923d2695e88c6400bf0c524b59737b508ea8f39b0ee8ef8486a2a6183b7811)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sparkEnvVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeys")
    def ssh_public_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshPublicKeys"))

    @ssh_public_keys.setter
    def ssh_public_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f18d3841371804c5d8e8656801444d8fe3d2de21ec7023db7692ffbfc1e954b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshPublicKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineCluster]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineCluster]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineCluster]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e41b430d976be56ffd57e79d96020dccc7707ca5072ff19eba520320cea75c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "allow_duplicate_names": "allowDuplicateNames",
        "budget_policy_id": "budgetPolicyId",
        "catalog": "catalog",
        "cause": "cause",
        "channel": "channel",
        "cluster": "cluster",
        "cluster_id": "clusterId",
        "configuration": "configuration",
        "continuous": "continuous",
        "creator_user_name": "creatorUserName",
        "deployment": "deployment",
        "development": "development",
        "edition": "edition",
        "environment": "environment",
        "event_log": "eventLog",
        "expected_last_modified": "expectedLastModified",
        "filters": "filters",
        "gateway_definition": "gatewayDefinition",
        "health": "health",
        "id": "id",
        "ingestion_definition": "ingestionDefinition",
        "last_modified": "lastModified",
        "latest_updates": "latestUpdates",
        "library": "library",
        "name": "name",
        "notification": "notification",
        "photon": "photon",
        "restart_window": "restartWindow",
        "root_path": "rootPath",
        "run_as": "runAs",
        "run_as_user_name": "runAsUserName",
        "schema": "schema",
        "serverless": "serverless",
        "state": "state",
        "storage": "storage",
        "tags": "tags",
        "target": "target",
        "timeouts": "timeouts",
        "trigger": "trigger",
        "url": "url",
    },
)
class PipelineConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allow_duplicate_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        budget_policy_id: typing.Optional[builtins.str] = None,
        catalog: typing.Optional[builtins.str] = None,
        cause: typing.Optional[builtins.str] = None,
        channel: typing.Optional[builtins.str] = None,
        cluster: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineCluster, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        configuration: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        continuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        creator_user_name: typing.Optional[builtins.str] = None,
        deployment: typing.Optional[typing.Union["PipelineDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        development: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        edition: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Union["PipelineEnvironment", typing.Dict[builtins.str, typing.Any]]] = None,
        event_log: typing.Optional[typing.Union["PipelineEventLog", typing.Dict[builtins.str, typing.Any]]] = None,
        expected_last_modified: typing.Optional[jsii.Number] = None,
        filters: typing.Optional[typing.Union["PipelineFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        gateway_definition: typing.Optional[typing.Union["PipelineGatewayDefinition", typing.Dict[builtins.str, typing.Any]]] = None,
        health: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ingestion_definition: typing.Optional[typing.Union["PipelineIngestionDefinition", typing.Dict[builtins.str, typing.Any]]] = None,
        last_modified: typing.Optional[jsii.Number] = None,
        latest_updates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLatestUpdates", typing.Dict[builtins.str, typing.Any]]]]] = None,
        library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineLibrary", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineNotification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        restart_window: typing.Optional[typing.Union["PipelineRestartWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        root_path: typing.Optional[builtins.str] = None,
        run_as: typing.Optional[typing.Union["PipelineRunAs", typing.Dict[builtins.str, typing.Any]]] = None,
        run_as_user_name: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        serverless: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        state: typing.Optional[builtins.str] = None,
        storage: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["PipelineTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        trigger: typing.Optional[typing.Union["PipelineTrigger", typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param allow_duplicate_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#allow_duplicate_names Pipeline#allow_duplicate_names}.
        :param budget_policy_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#budget_policy_id Pipeline#budget_policy_id}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.
        :param cause: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cause Pipeline#cause}.
        :param channel: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#channel Pipeline#channel}.
        :param cluster: cluster block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster Pipeline#cluster}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster_id Pipeline#cluster_id}.
        :param configuration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#configuration Pipeline#configuration}.
        :param continuous: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#continuous Pipeline#continuous}.
        :param creator_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#creator_user_name Pipeline#creator_user_name}.
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deployment Pipeline#deployment}
        :param development: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#development Pipeline#development}.
        :param edition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#edition Pipeline#edition}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#environment Pipeline#environment}
        :param event_log: event_log block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#event_log Pipeline#event_log}
        :param expected_last_modified: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#expected_last_modified Pipeline#expected_last_modified}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#filters Pipeline#filters}
        :param gateway_definition: gateway_definition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_definition Pipeline#gateway_definition}
        :param health: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#health Pipeline#health}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#id Pipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingestion_definition: ingestion_definition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_definition Pipeline#ingestion_definition}
        :param last_modified: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#last_modified Pipeline#last_modified}.
        :param latest_updates: latest_updates block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#latest_updates Pipeline#latest_updates}
        :param library: library block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#library Pipeline#library}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#notification Pipeline#notification}
        :param photon: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#photon Pipeline#photon}.
        :param restart_window: restart_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#restart_window Pipeline#restart_window}
        :param root_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#root_path Pipeline#root_path}.
        :param run_as: run_as block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as Pipeline#run_as}
        :param run_as_user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as_user_name Pipeline#run_as_user_name}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.
        :param serverless: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#serverless Pipeline#serverless}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#state Pipeline#state}.
        :param storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#storage Pipeline#storage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#tags Pipeline#tags}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#target Pipeline#target}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timeouts Pipeline#timeouts}
        :param trigger: trigger block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#trigger Pipeline#trigger}
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#url Pipeline#url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = PipelineDeployment(**deployment)
        if isinstance(environment, dict):
            environment = PipelineEnvironment(**environment)
        if isinstance(event_log, dict):
            event_log = PipelineEventLog(**event_log)
        if isinstance(filters, dict):
            filters = PipelineFilters(**filters)
        if isinstance(gateway_definition, dict):
            gateway_definition = PipelineGatewayDefinition(**gateway_definition)
        if isinstance(ingestion_definition, dict):
            ingestion_definition = PipelineIngestionDefinition(**ingestion_definition)
        if isinstance(restart_window, dict):
            restart_window = PipelineRestartWindow(**restart_window)
        if isinstance(run_as, dict):
            run_as = PipelineRunAs(**run_as)
        if isinstance(timeouts, dict):
            timeouts = PipelineTimeouts(**timeouts)
        if isinstance(trigger, dict):
            trigger = PipelineTrigger(**trigger)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6187572c5ad940dfd5a25a138b6dd12be1d616cdc158bddc0762499407f2b92a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument allow_duplicate_names", value=allow_duplicate_names, expected_type=type_hints["allow_duplicate_names"])
            check_type(argname="argument budget_policy_id", value=budget_policy_id, expected_type=type_hints["budget_policy_id"])
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
            check_type(argname="argument cause", value=cause, expected_type=type_hints["cause"])
            check_type(argname="argument channel", value=channel, expected_type=type_hints["channel"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument continuous", value=continuous, expected_type=type_hints["continuous"])
            check_type(argname="argument creator_user_name", value=creator_user_name, expected_type=type_hints["creator_user_name"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument development", value=development, expected_type=type_hints["development"])
            check_type(argname="argument edition", value=edition, expected_type=type_hints["edition"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument event_log", value=event_log, expected_type=type_hints["event_log"])
            check_type(argname="argument expected_last_modified", value=expected_last_modified, expected_type=type_hints["expected_last_modified"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument gateway_definition", value=gateway_definition, expected_type=type_hints["gateway_definition"])
            check_type(argname="argument health", value=health, expected_type=type_hints["health"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ingestion_definition", value=ingestion_definition, expected_type=type_hints["ingestion_definition"])
            check_type(argname="argument last_modified", value=last_modified, expected_type=type_hints["last_modified"])
            check_type(argname="argument latest_updates", value=latest_updates, expected_type=type_hints["latest_updates"])
            check_type(argname="argument library", value=library, expected_type=type_hints["library"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument notification", value=notification, expected_type=type_hints["notification"])
            check_type(argname="argument photon", value=photon, expected_type=type_hints["photon"])
            check_type(argname="argument restart_window", value=restart_window, expected_type=type_hints["restart_window"])
            check_type(argname="argument root_path", value=root_path, expected_type=type_hints["root_path"])
            check_type(argname="argument run_as", value=run_as, expected_type=type_hints["run_as"])
            check_type(argname="argument run_as_user_name", value=run_as_user_name, expected_type=type_hints["run_as_user_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument serverless", value=serverless, expected_type=type_hints["serverless"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument storage", value=storage, expected_type=type_hints["storage"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument trigger", value=trigger, expected_type=type_hints["trigger"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
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
        if allow_duplicate_names is not None:
            self._values["allow_duplicate_names"] = allow_duplicate_names
        if budget_policy_id is not None:
            self._values["budget_policy_id"] = budget_policy_id
        if catalog is not None:
            self._values["catalog"] = catalog
        if cause is not None:
            self._values["cause"] = cause
        if channel is not None:
            self._values["channel"] = channel
        if cluster is not None:
            self._values["cluster"] = cluster
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if configuration is not None:
            self._values["configuration"] = configuration
        if continuous is not None:
            self._values["continuous"] = continuous
        if creator_user_name is not None:
            self._values["creator_user_name"] = creator_user_name
        if deployment is not None:
            self._values["deployment"] = deployment
        if development is not None:
            self._values["development"] = development
        if edition is not None:
            self._values["edition"] = edition
        if environment is not None:
            self._values["environment"] = environment
        if event_log is not None:
            self._values["event_log"] = event_log
        if expected_last_modified is not None:
            self._values["expected_last_modified"] = expected_last_modified
        if filters is not None:
            self._values["filters"] = filters
        if gateway_definition is not None:
            self._values["gateway_definition"] = gateway_definition
        if health is not None:
            self._values["health"] = health
        if id is not None:
            self._values["id"] = id
        if ingestion_definition is not None:
            self._values["ingestion_definition"] = ingestion_definition
        if last_modified is not None:
            self._values["last_modified"] = last_modified
        if latest_updates is not None:
            self._values["latest_updates"] = latest_updates
        if library is not None:
            self._values["library"] = library
        if name is not None:
            self._values["name"] = name
        if notification is not None:
            self._values["notification"] = notification
        if photon is not None:
            self._values["photon"] = photon
        if restart_window is not None:
            self._values["restart_window"] = restart_window
        if root_path is not None:
            self._values["root_path"] = root_path
        if run_as is not None:
            self._values["run_as"] = run_as
        if run_as_user_name is not None:
            self._values["run_as_user_name"] = run_as_user_name
        if schema is not None:
            self._values["schema"] = schema
        if serverless is not None:
            self._values["serverless"] = serverless
        if state is not None:
            self._values["state"] = state
        if storage is not None:
            self._values["storage"] = storage
        if tags is not None:
            self._values["tags"] = tags
        if target is not None:
            self._values["target"] = target
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if trigger is not None:
            self._values["trigger"] = trigger
        if url is not None:
            self._values["url"] = url

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
    def allow_duplicate_names(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#allow_duplicate_names Pipeline#allow_duplicate_names}.'''
        result = self._values.get("allow_duplicate_names")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def budget_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#budget_policy_id Pipeline#budget_policy_id}.'''
        result = self._values.get("budget_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.'''
        result = self._values.get("catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cause(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cause Pipeline#cause}.'''
        result = self._values.get("cause")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#channel Pipeline#channel}.'''
        result = self._values.get("channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]]:
        '''cluster block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster Pipeline#cluster}
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cluster_id Pipeline#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#configuration Pipeline#configuration}.'''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def continuous(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#continuous Pipeline#continuous}.'''
        result = self._values.get("continuous")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def creator_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#creator_user_name Pipeline#creator_user_name}.'''
        result = self._values.get("creator_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment(self) -> typing.Optional["PipelineDeployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deployment Pipeline#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["PipelineDeployment"], result)

    @builtins.property
    def development(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#development Pipeline#development}.'''
        result = self._values.get("development")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def edition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#edition Pipeline#edition}.'''
        result = self._values.get("edition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional["PipelineEnvironment"]:
        '''environment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#environment Pipeline#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional["PipelineEnvironment"], result)

    @builtins.property
    def event_log(self) -> typing.Optional["PipelineEventLog"]:
        '''event_log block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#event_log Pipeline#event_log}
        '''
        result = self._values.get("event_log")
        return typing.cast(typing.Optional["PipelineEventLog"], result)

    @builtins.property
    def expected_last_modified(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#expected_last_modified Pipeline#expected_last_modified}.'''
        result = self._values.get("expected_last_modified")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def filters(self) -> typing.Optional["PipelineFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#filters Pipeline#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["PipelineFilters"], result)

    @builtins.property
    def gateway_definition(self) -> typing.Optional["PipelineGatewayDefinition"]:
        '''gateway_definition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_definition Pipeline#gateway_definition}
        '''
        result = self._values.get("gateway_definition")
        return typing.cast(typing.Optional["PipelineGatewayDefinition"], result)

    @builtins.property
    def health(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#health Pipeline#health}.'''
        result = self._values.get("health")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#id Pipeline#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingestion_definition(self) -> typing.Optional["PipelineIngestionDefinition"]:
        '''ingestion_definition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_definition Pipeline#ingestion_definition}
        '''
        result = self._values.get("ingestion_definition")
        return typing.cast(typing.Optional["PipelineIngestionDefinition"], result)

    @builtins.property
    def last_modified(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#last_modified Pipeline#last_modified}.'''
        result = self._values.get("last_modified")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def latest_updates(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLatestUpdates"]]]:
        '''latest_updates block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#latest_updates Pipeline#latest_updates}
        '''
        result = self._values.get("latest_updates")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLatestUpdates"]]], result)

    @builtins.property
    def library(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLibrary"]]]:
        '''library block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#library Pipeline#library}
        '''
        result = self._values.get("library")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineLibrary"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineNotification"]]]:
        '''notification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#notification Pipeline#notification}
        '''
        result = self._values.get("notification")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineNotification"]]], result)

    @builtins.property
    def photon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#photon Pipeline#photon}.'''
        result = self._values.get("photon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def restart_window(self) -> typing.Optional["PipelineRestartWindow"]:
        '''restart_window block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#restart_window Pipeline#restart_window}
        '''
        result = self._values.get("restart_window")
        return typing.cast(typing.Optional["PipelineRestartWindow"], result)

    @builtins.property
    def root_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#root_path Pipeline#root_path}.'''
        result = self._values.get("root_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_as(self) -> typing.Optional["PipelineRunAs"]:
        '''run_as block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as Pipeline#run_as}
        '''
        result = self._values.get("run_as")
        return typing.cast(typing.Optional["PipelineRunAs"], result)

    @builtins.property
    def run_as_user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#run_as_user_name Pipeline#run_as_user_name}.'''
        result = self._values.get("run_as_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serverless(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#serverless Pipeline#serverless}.'''
        result = self._values.get("serverless")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#state Pipeline#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#storage Pipeline#storage}.'''
        result = self._values.get("storage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#tags Pipeline#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#target Pipeline#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["PipelineTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timeouts Pipeline#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["PipelineTimeouts"], result)

    @builtins.property
    def trigger(self) -> typing.Optional["PipelineTrigger"]:
        '''trigger block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#trigger Pipeline#trigger}
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["PipelineTrigger"], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#url Pipeline#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineDeployment",
    jsii_struct_bases=[],
    name_mapping={"kind": "kind", "metadata_file_path": "metadataFilePath"},
)
class PipelineDeployment:
    def __init__(
        self,
        *,
        kind: builtins.str,
        metadata_file_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param kind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kind Pipeline#kind}.
        :param metadata_file_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#metadata_file_path Pipeline#metadata_file_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d457cf4da02af0dcea95b07a13bdf3cf3b9471e9120e11e8e9a6be9d670df7d0)
            check_type(argname="argument kind", value=kind, expected_type=type_hints["kind"])
            check_type(argname="argument metadata_file_path", value=metadata_file_path, expected_type=type_hints["metadata_file_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kind": kind,
        }
        if metadata_file_path is not None:
            self._values["metadata_file_path"] = metadata_file_path

    @builtins.property
    def kind(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#kind Pipeline#kind}.'''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metadata_file_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#metadata_file_path Pipeline#metadata_file_path}.'''
        result = self._values.get("metadata_file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bda9c79fbe2101594798ef8fc2905fdea574d0af8d9b5baebfcb16c2bd3d09d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMetadataFilePath")
    def reset_metadata_file_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadataFilePath", []))

    @builtins.property
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataFilePathInput")
    def metadata_file_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataFilePathInput"))

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60b68318c0559e3ae0ac60f391ab4f882350354565b31c687a3f7269e39a23d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadataFilePath")
    def metadata_file_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metadataFilePath"))

    @metadata_file_path.setter
    def metadata_file_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a372a4576f1e503f599f01421bac7e56d0823d3f0a1cb24c17134930107f2b56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadataFilePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineDeployment]:
        return typing.cast(typing.Optional[PipelineDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineDeployment]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__120a1900efb40d496ff1b69fb79a1d6c022a6710437cefd350642a1152cb3472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineEnvironment",
    jsii_struct_bases=[],
    name_mapping={"dependencies": "dependencies"},
)
class PipelineEnvironment:
    def __init__(
        self,
        *,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param dependencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dependencies Pipeline#dependencies}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70b1a3dfa0971b7c9b0a277f714540601dff9b5482131841d699c6c4a84013dc)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dependencies is not None:
            self._values["dependencies"] = dependencies

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#dependencies Pipeline#dependencies}.'''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineEnvironmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineEnvironmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cce8c58d8101a6fb86b9b8c9d65b645a79a4756d84088f1c4b6e8d2d232edfbe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDependencies")
    def reset_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="dependenciesInput")
    def dependencies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14051ab6e8ca902385d97b381b4396655123008e72755c704140d8f2bf262294)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineEnvironment]:
        return typing.cast(typing.Optional[PipelineEnvironment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineEnvironment]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cabd13e3005ef8be7802d157d2550ed58695e8edf7de5502ade42bc23330da4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineEventLog",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "catalog": "catalog", "schema": "schema"},
)
class PipelineEventLog:
    def __init__(
        self,
        *,
        name: builtins.str,
        catalog: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.
        :param catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.
        :param schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0bdc19b18f717a6cf77b78ea815f6911b427795e0ca1fd5d5e254af21afdd1)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if catalog is not None:
            self._values["catalog"] = catalog
        if schema is not None:
            self._values["schema"] = schema

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#name Pipeline#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}.'''
        result = self._values.get("catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineEventLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineEventLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineEventLogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c0598f74fe1435002dec9c55445611b662e1d2bb4f83734d80cadae801f72cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCatalog")
    def reset_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalog", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @builtins.property
    @jsii.member(jsii_name="catalogInput")
    def catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="catalog")
    def catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "catalog"))

    @catalog.setter
    def catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__519e505eb78e6a0d93936ff36835b4c5b01bf8ee55e225bcccc679fa0218d18b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "catalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fdac64802addc073b7c2c7cdd62a716f9620713aad9a19f19fc4a0c37607d75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6347ff3985dd38629c6eef5e2c7cbac9d6b5cd4ab1b80ae3ef50b7a12232934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineEventLog]:
        return typing.cast(typing.Optional[PipelineEventLog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineEventLog]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8874367918c58253277f6d41f07dd52d6e184d6b293fbc6cb7b4a68a32105947)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineFilters",
    jsii_struct_bases=[],
    name_mapping={"exclude": "exclude", "include": "include"},
)
class PipelineFilters:
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude Pipeline#exclude}.
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64638efb34092d970f979aa95dda37b337a35c8d4409b1048d5fb62a1c5f7018)
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude Pipeline#exclude}.'''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.'''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0891539faccb9bce1a5c612ff798c286b2b2afb19f19cfdd0cc0c638ee14ee15)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExclude")
    def reset_exclude(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclude", []))

    @jsii.member(jsii_name="resetInclude")
    def reset_include(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInclude", []))

    @builtins.property
    @jsii.member(jsii_name="excludeInput")
    def exclude_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeInput"))

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9909dfe2ca81ce429b712d30c404f46bf95aa9909c429d2ae7c7128271bac44f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__299e91eb4a5a518a5fd257ec4d46cdf8f4b82efd9ca802e8702e5cd218d95b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineFilters]:
        return typing.cast(typing.Optional[PipelineFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineFilters]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64895675f014f00616dc9ca02330c00c7475651b79bc03084118f9cc35261590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineGatewayDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "connection_name": "connectionName",
        "gateway_storage_catalog": "gatewayStorageCatalog",
        "gateway_storage_schema": "gatewayStorageSchema",
        "connection_id": "connectionId",
        "gateway_storage_name": "gatewayStorageName",
    },
)
class PipelineGatewayDefinition:
    def __init__(
        self,
        *,
        connection_name: builtins.str,
        gateway_storage_catalog: builtins.str,
        gateway_storage_schema: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
        gateway_storage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.
        :param gateway_storage_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_catalog Pipeline#gateway_storage_catalog}.
        :param gateway_storage_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_schema Pipeline#gateway_storage_schema}.
        :param connection_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_id Pipeline#connection_id}.
        :param gateway_storage_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_name Pipeline#gateway_storage_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62fdefe8d555d1f3c86cc11cfa20788f1ac8f0d0d867286c8da364fef6be9ed5)
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument gateway_storage_catalog", value=gateway_storage_catalog, expected_type=type_hints["gateway_storage_catalog"])
            check_type(argname="argument gateway_storage_schema", value=gateway_storage_schema, expected_type=type_hints["gateway_storage_schema"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument gateway_storage_name", value=gateway_storage_name, expected_type=type_hints["gateway_storage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_name": connection_name,
            "gateway_storage_catalog": gateway_storage_catalog,
            "gateway_storage_schema": gateway_storage_schema,
        }
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if gateway_storage_name is not None:
            self._values["gateway_storage_name"] = gateway_storage_name

    @builtins.property
    def connection_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.'''
        result = self._values.get("connection_name")
        assert result is not None, "Required property 'connection_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_storage_catalog(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_catalog Pipeline#gateway_storage_catalog}.'''
        result = self._values.get("gateway_storage_catalog")
        assert result is not None, "Required property 'gateway_storage_catalog' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_storage_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_schema Pipeline#gateway_storage_schema}.'''
        result = self._values.get("gateway_storage_schema")
        assert result is not None, "Required property 'gateway_storage_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_id Pipeline#connection_id}.'''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateway_storage_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#gateway_storage_name Pipeline#gateway_storage_name}.'''
        result = self._values.get("gateway_storage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineGatewayDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineGatewayDefinitionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineGatewayDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__03d6be8612081073eaf87ab80bff24230daa9878d941a0b99735a120c0aa6d02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionId")
    def reset_connection_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionId", []))

    @jsii.member(jsii_name="resetGatewayStorageName")
    def reset_gateway_storage_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayStorageName", []))

    @builtins.property
    @jsii.member(jsii_name="connectionIdInput")
    def connection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionNameInput")
    def connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageCatalogInput")
    def gateway_storage_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayStorageCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageNameInput")
    def gateway_storage_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayStorageNameInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageSchemaInput")
    def gateway_storage_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayStorageSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08fbac6aeaaee351e5939e793e11d265e61ed054dd88da275b7cbbc57b82ab69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e14d00a3cec6b23b09d220a6c19490feab5745928629a0b212df0952e41cbe85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageCatalog")
    def gateway_storage_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayStorageCatalog"))

    @gateway_storage_catalog.setter
    def gateway_storage_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b5e5fae784fd38aca2fdcde3b6b2e87e9b797a681c3f6172ff31a965a3e0604)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewayStorageCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageName")
    def gateway_storage_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayStorageName"))

    @gateway_storage_name.setter
    def gateway_storage_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b07b7214443f4e23f4879fa4f49f49c737e55dc1c83ea14b1943826f16152ad8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewayStorageName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gatewayStorageSchema")
    def gateway_storage_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayStorageSchema"))

    @gateway_storage_schema.setter
    def gateway_storage_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d50b4aec9c1273e2523d6c78cdd5b4d31dfaee28037fac055bfb5c4eaf39384)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewayStorageSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineGatewayDefinition]:
        return typing.cast(typing.Optional[PipelineGatewayDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineGatewayDefinition]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec2a294dd6088a2744ff373dabc7edbda043e40d820269b2d1a708b8617e8c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "connection_name": "connectionName",
        "ingestion_gateway_id": "ingestionGatewayId",
        "objects": "objects",
        "source_configurations": "sourceConfigurations",
        "source_type": "sourceType",
        "table_configuration": "tableConfiguration",
    },
)
class PipelineIngestionDefinition:
    def __init__(
        self,
        *,
        connection_name: typing.Optional[builtins.str] = None,
        ingestion_gateway_id: typing.Optional[builtins.str] = None,
        objects: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineIngestionDefinitionObjects", typing.Dict[builtins.str, typing.Any]]]]] = None,
        source_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineIngestionDefinitionSourceConfigurations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        source_type: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.
        :param ingestion_gateway_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_gateway_id Pipeline#ingestion_gateway_id}.
        :param objects: objects block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#objects Pipeline#objects}
        :param source_configurations: source_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_configurations Pipeline#source_configurations}
        :param source_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_type Pipeline#source_type}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        if isinstance(table_configuration, dict):
            table_configuration = PipelineIngestionDefinitionTableConfiguration(**table_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe1fdce8b61ef4e74dfb9137f6efdcf51c918322211bca74faac92bc6c1d557)
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument ingestion_gateway_id", value=ingestion_gateway_id, expected_type=type_hints["ingestion_gateway_id"])
            check_type(argname="argument objects", value=objects, expected_type=type_hints["objects"])
            check_type(argname="argument source_configurations", value=source_configurations, expected_type=type_hints["source_configurations"])
            check_type(argname="argument source_type", value=source_type, expected_type=type_hints["source_type"])
            check_type(argname="argument table_configuration", value=table_configuration, expected_type=type_hints["table_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_name is not None:
            self._values["connection_name"] = connection_name
        if ingestion_gateway_id is not None:
            self._values["ingestion_gateway_id"] = ingestion_gateway_id
        if objects is not None:
            self._values["objects"] = objects
        if source_configurations is not None:
            self._values["source_configurations"] = source_configurations
        if source_type is not None:
            self._values["source_type"] = source_type
        if table_configuration is not None:
            self._values["table_configuration"] = table_configuration

    @builtins.property
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#connection_name Pipeline#connection_name}.'''
        result = self._values.get("connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingestion_gateway_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#ingestion_gateway_id Pipeline#ingestion_gateway_id}.'''
        result = self._values.get("ingestion_gateway_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def objects(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionObjects"]]]:
        '''objects block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#objects Pipeline#objects}
        '''
        result = self._values.get("objects")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionObjects"]]], result)

    @builtins.property
    def source_configurations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionSourceConfigurations"]]]:
        '''source_configurations block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_configurations Pipeline#source_configurations}
        '''
        result = self._values.get("source_configurations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionSourceConfigurations"]]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_type Pipeline#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_configuration(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionTableConfiguration"]:
        '''table_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        result = self._values.get("table_configuration")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionTableConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjects",
    jsii_struct_bases=[],
    name_mapping={"report": "report", "schema": "schema", "table": "table"},
)
class PipelineIngestionDefinitionObjects:
    def __init__(
        self,
        *,
        report: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsReport", typing.Dict[builtins.str, typing.Any]]] = None,
        schema: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsSchema", typing.Dict[builtins.str, typing.Any]]] = None,
        table: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsTable", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param report: report block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#report Pipeline#report}
        :param schema: schema block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}
        :param table: table block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table Pipeline#table}
        '''
        if isinstance(report, dict):
            report = PipelineIngestionDefinitionObjectsReport(**report)
        if isinstance(schema, dict):
            schema = PipelineIngestionDefinitionObjectsSchema(**schema)
        if isinstance(table, dict):
            table = PipelineIngestionDefinitionObjectsTable(**table)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__265b42cd2ddb3b636903e241e8d396b9155f0377d733cc091b479ba1bf937a8c)
            check_type(argname="argument report", value=report, expected_type=type_hints["report"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if report is not None:
            self._values["report"] = report
        if schema is not None:
            self._values["schema"] = schema
        if table is not None:
            self._values["table"] = table

    @builtins.property
    def report(self) -> typing.Optional["PipelineIngestionDefinitionObjectsReport"]:
        '''report block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#report Pipeline#report}
        '''
        result = self._values.get("report")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReport"], result)

    @builtins.property
    def schema(self) -> typing.Optional["PipelineIngestionDefinitionObjectsSchema"]:
        '''schema block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#schema Pipeline#schema}
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchema"], result)

    @builtins.property
    def table(self) -> typing.Optional["PipelineIngestionDefinitionObjectsTable"]:
        '''table block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table Pipeline#table}
        '''
        result = self._values.get("table")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTable"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjects(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81dc6b11f002d166b909f8ea967fe8084730b8c48af61b4dcd83b1de52709ef5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PipelineIngestionDefinitionObjectsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d4b7c685ce1a02873f60de570c7dbed108019260ed31216c18acdb7946440fd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineIngestionDefinitionObjectsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa6de567f178301ba4950a226ee9439adce0d8e365bb46db1344821632c89b7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b61b4a5aa213b74c58efd45b42e6353fb9dc310b6fee2dcb993f57c738ca223d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7a3ad75aea51f7ac0d7dac461e6c5e193cc7a464358b4cd7e4341423eef8690)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b59b7c1fda0699797b64248b5b696287f1fe2a9f9ce9b98f141dcd173be29162)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineIngestionDefinitionObjectsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d6eb0040d9147852bf2b6698801eb5215c22db5ff257207b587aaad0ecef4e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putReport")
    def put_report(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_url: builtins.str,
        destination_table: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsReportTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_url Pipeline#source_url}.
        :param destination_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        value = PipelineIngestionDefinitionObjectsReport(
            destination_catalog=destination_catalog,
            destination_schema=destination_schema,
            source_url=source_url,
            destination_table=destination_table,
            table_configuration=table_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putReport", [value]))

    @jsii.member(jsii_name="putSchema")
    def put_schema(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_schema: builtins.str,
        source_catalog: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsSchemaTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        value = PipelineIngestionDefinitionObjectsSchema(
            destination_catalog=destination_catalog,
            destination_schema=destination_schema,
            source_schema=source_schema,
            source_catalog=source_catalog,
            table_configuration=table_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putSchema", [value]))

    @jsii.member(jsii_name="putTable")
    def put_table(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_table: builtins.str,
        destination_table: typing.Optional[builtins.str] = None,
        source_catalog: typing.Optional[builtins.str] = None,
        source_schema: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsTableTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_table Pipeline#source_table}.
        :param destination_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        :param source_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        value = PipelineIngestionDefinitionObjectsTable(
            destination_catalog=destination_catalog,
            destination_schema=destination_schema,
            source_table=source_table,
            destination_table=destination_table,
            source_catalog=source_catalog,
            source_schema=source_schema,
            table_configuration=table_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putTable", [value]))

    @jsii.member(jsii_name="resetReport")
    def reset_report(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReport", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetTable")
    def reset_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTable", []))

    @builtins.property
    @jsii.member(jsii_name="report")
    def report(self) -> "PipelineIngestionDefinitionObjectsReportOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsReportOutputReference", jsii.get(self, "report"))

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> "PipelineIngestionDefinitionObjectsSchemaOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsSchemaOutputReference", jsii.get(self, "schema"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> "PipelineIngestionDefinitionObjectsTableOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsTableOutputReference", jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="reportInput")
    def report_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsReport"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReport"], jsii.get(self, "reportInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsSchema"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchema"], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="tableInput")
    def table_input(self) -> typing.Optional["PipelineIngestionDefinitionObjectsTable"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTable"], jsii.get(self, "tableInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionObjects]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionObjects]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionObjects]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__687ed40e742f23c98329291f62d12a608ff61d7b7618446f9ba27204f6ebccb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReport",
    jsii_struct_bases=[],
    name_mapping={
        "destination_catalog": "destinationCatalog",
        "destination_schema": "destinationSchema",
        "source_url": "sourceUrl",
        "destination_table": "destinationTable",
        "table_configuration": "tableConfiguration",
    },
)
class PipelineIngestionDefinitionObjectsReport:
    def __init__(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_url: builtins.str,
        destination_table: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsReportTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_url Pipeline#source_url}.
        :param destination_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        if isinstance(table_configuration, dict):
            table_configuration = PipelineIngestionDefinitionObjectsReportTableConfiguration(**table_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d780f9caccab1364ee4a86d0e87f1b5b0392946aaacdb617420e52613e2cf7ef)
            check_type(argname="argument destination_catalog", value=destination_catalog, expected_type=type_hints["destination_catalog"])
            check_type(argname="argument destination_schema", value=destination_schema, expected_type=type_hints["destination_schema"])
            check_type(argname="argument source_url", value=source_url, expected_type=type_hints["source_url"])
            check_type(argname="argument destination_table", value=destination_table, expected_type=type_hints["destination_table"])
            check_type(argname="argument table_configuration", value=table_configuration, expected_type=type_hints["table_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination_catalog": destination_catalog,
            "destination_schema": destination_schema,
            "source_url": source_url,
        }
        if destination_table is not None:
            self._values["destination_table"] = destination_table
        if table_configuration is not None:
            self._values["table_configuration"] = table_configuration

    @builtins.property
    def destination_catalog(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.'''
        result = self._values.get("destination_catalog")
        assert result is not None, "Required property 'destination_catalog' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.'''
        result = self._values.get("destination_schema")
        assert result is not None, "Required property 'destination_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_url Pipeline#source_url}.'''
        result = self._values.get("source_url")
        assert result is not None, "Required property 'source_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_table(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.'''
        result = self._values.get("destination_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_configuration(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfiguration"]:
        '''table_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        result = self._values.get("table_configuration")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsReport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsReportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ca2d7dc70c762115d0b0421ee4261199e2de1aa8d0c6983f61fae48f51a0abd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTableConfiguration")
    def put_table_configuration(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        value = PipelineIngestionDefinitionObjectsReportTableConfiguration(
            exclude_columns=exclude_columns,
            include_columns=include_columns,
            primary_keys=primary_keys,
            query_based_connector_config=query_based_connector_config,
            salesforce_include_formula_fields=salesforce_include_formula_fields,
            scd_type=scd_type,
            sequence_by=sequence_by,
        )

        return typing.cast(None, jsii.invoke(self, "putTableConfiguration", [value]))

    @jsii.member(jsii_name="resetDestinationTable")
    def reset_destination_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationTable", []))

    @jsii.member(jsii_name="resetTableConfiguration")
    def reset_table_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConfiguration", []))

    @builtins.property
    @jsii.member(jsii_name="tableConfiguration")
    def table_configuration(
        self,
    ) -> "PipelineIngestionDefinitionObjectsReportTableConfigurationOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsReportTableConfigurationOutputReference", jsii.get(self, "tableConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalogInput")
    def destination_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationSchemaInput")
    def destination_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationTableInput")
    def destination_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationTableInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceUrlInput")
    def source_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConfigurationInput")
    def table_configuration_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfiguration"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfiguration"], jsii.get(self, "tableConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalog")
    def destination_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationCatalog"))

    @destination_catalog.setter
    def destination_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a14d2cc134bc361bb756c6bbe91ecb8ae5a80397b22871e03b69411946a5f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationSchema")
    def destination_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationSchema"))

    @destination_schema.setter
    def destination_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b1fc2d185c744ff1f12d6aa06cfb723e4a987b61fa3705e8e74029f01e82607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationTable")
    def destination_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationTable"))

    @destination_table.setter
    def destination_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072ca0cddccaaff2ecc9b5e236d51512648b2ab7378e0d55e05c92ce04835528)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUrl"))

    @source_url.setter
    def source_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afc6316a3fc3cba550f257e77786bf1cc0099904b058be0da466f51e568571e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsReport]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsReport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsReport],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b45d886fc6f34d41facbcc89ace49119892546938fae14c51c6211471da298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReportTableConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_columns": "excludeColumns",
        "include_columns": "includeColumns",
        "primary_keys": "primaryKeys",
        "query_based_connector_config": "queryBasedConnectorConfig",
        "salesforce_include_formula_fields": "salesforceIncludeFormulaFields",
        "scd_type": "scdType",
        "sequence_by": "sequenceBy",
    },
)
class PipelineIngestionDefinitionObjectsReportTableConfiguration:
    def __init__(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        if isinstance(query_based_connector_config, dict):
            query_based_connector_config = PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig(**query_based_connector_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2ae4cecf709d650d294c4de42738d039f3c89709ca82224e454e920a8b22675)
            check_type(argname="argument exclude_columns", value=exclude_columns, expected_type=type_hints["exclude_columns"])
            check_type(argname="argument include_columns", value=include_columns, expected_type=type_hints["include_columns"])
            check_type(argname="argument primary_keys", value=primary_keys, expected_type=type_hints["primary_keys"])
            check_type(argname="argument query_based_connector_config", value=query_based_connector_config, expected_type=type_hints["query_based_connector_config"])
            check_type(argname="argument salesforce_include_formula_fields", value=salesforce_include_formula_fields, expected_type=type_hints["salesforce_include_formula_fields"])
            check_type(argname="argument scd_type", value=scd_type, expected_type=type_hints["scd_type"])
            check_type(argname="argument sequence_by", value=sequence_by, expected_type=type_hints["sequence_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_columns is not None:
            self._values["exclude_columns"] = exclude_columns
        if include_columns is not None:
            self._values["include_columns"] = include_columns
        if primary_keys is not None:
            self._values["primary_keys"] = primary_keys
        if query_based_connector_config is not None:
            self._values["query_based_connector_config"] = query_based_connector_config
        if salesforce_include_formula_fields is not None:
            self._values["salesforce_include_formula_fields"] = salesforce_include_formula_fields
        if scd_type is not None:
            self._values["scd_type"] = scd_type
        if sequence_by is not None:
            self._values["sequence_by"] = sequence_by

    @builtins.property
    def exclude_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.'''
        result = self._values.get("exclude_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.'''
        result = self._values.get("include_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def primary_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.'''
        result = self._values.get("primary_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_based_connector_config(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig"]:
        '''query_based_connector_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        '''
        result = self._values.get("query_based_connector_config")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig"], result)

    @builtins.property
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.'''
        result = self._values.get("salesforce_include_formula_fields")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def scd_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.'''
        result = self._values.get("scd_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sequence_by(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.'''
        result = self._values.get("sequence_by")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsReportTableConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsReportTableConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReportTableConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__057156336f7490bd1ecfc4cc3e83b20fa525ee8fb7cbc716554536d9232f277e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putQueryBasedConnectorConfig")
    def put_query_based_connector_config(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        value = PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig(
            cursor_columns=cursor_columns,
            deletion_condition=deletion_condition,
            hard_deletion_sync_min_interval_in_seconds=hard_deletion_sync_min_interval_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putQueryBasedConnectorConfig", [value]))

    @jsii.member(jsii_name="resetExcludeColumns")
    def reset_exclude_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeColumns", []))

    @jsii.member(jsii_name="resetIncludeColumns")
    def reset_include_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeColumns", []))

    @jsii.member(jsii_name="resetPrimaryKeys")
    def reset_primary_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeys", []))

    @jsii.member(jsii_name="resetQueryBasedConnectorConfig")
    def reset_query_based_connector_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryBasedConnectorConfig", []))

    @jsii.member(jsii_name="resetSalesforceIncludeFormulaFields")
    def reset_salesforce_include_formula_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSalesforceIncludeFormulaFields", []))

    @jsii.member(jsii_name="resetScdType")
    def reset_scd_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScdType", []))

    @jsii.member(jsii_name="resetSequenceBy")
    def reset_sequence_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSequenceBy", []))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfig")
    def query_based_connector_config(
        self,
    ) -> "PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfigOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfigOutputReference", jsii.get(self, "queryBasedConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumnsInput")
    def exclude_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeColumnsInput")
    def include_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeysInput")
    def primary_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfigInput")
    def query_based_connector_config_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig"], jsii.get(self, "queryBasedConnectorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFieldsInput")
    def salesforce_include_formula_fields_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "salesforceIncludeFormulaFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="scdTypeInput")
    def scd_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scdTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sequenceByInput")
    def sequence_by_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sequenceByInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumns")
    def exclude_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeColumns"))

    @exclude_columns.setter
    def exclude_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b85125af5ae84291015caa19d2d70ffd2c41ec69e4d7cd4cda15478324d2aed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeColumns")
    def include_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeColumns"))

    @include_columns.setter
    def include_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e64bfb064a59d59b998a543b25b9724822a9342c0faa2d5c85bce1d5a47edec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeys")
    def primary_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeys"))

    @primary_keys.setter
    def primary_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc0d3e609859c341e5448a20f1bcd1ba5d140114dedb0e13ee67e04415511122)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFields")
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "salesforceIncludeFormulaFields"))

    @salesforce_include_formula_fields.setter
    def salesforce_include_formula_fields(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af8663b2f1a8b931b76a65454814ef96a7f0b1f83c7dca646514da924399ef96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "salesforceIncludeFormulaFields", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scdType")
    def scd_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scdType"))

    @scd_type.setter
    def scd_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06bf4aa3a3e3674c180e165c0b9bd7d260721d76c3998db5415f65b4ff2131cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scdType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequenceBy")
    def sequence_by(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sequenceBy"))

    @sequence_by.setter
    def sequence_by(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05e7f53fa4849fbe677fd07802d6fa2656393f42014bd4358617784abc7a832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequenceBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfiguration]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59951f71b7b156efc2f322ece1654be2de818ccae8cd357343d5253e71b64ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cursor_columns": "cursorColumns",
        "deletion_condition": "deletionCondition",
        "hard_deletion_sync_min_interval_in_seconds": "hardDeletionSyncMinIntervalInSeconds",
    },
)
class PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig:
    def __init__(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d0a4f8df42bfadcb83acd828b9d2a3f407fb9db1f136ae3d88e69f7952931df)
            check_type(argname="argument cursor_columns", value=cursor_columns, expected_type=type_hints["cursor_columns"])
            check_type(argname="argument deletion_condition", value=deletion_condition, expected_type=type_hints["deletion_condition"])
            check_type(argname="argument hard_deletion_sync_min_interval_in_seconds", value=hard_deletion_sync_min_interval_in_seconds, expected_type=type_hints["hard_deletion_sync_min_interval_in_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cursor_columns is not None:
            self._values["cursor_columns"] = cursor_columns
        if deletion_condition is not None:
            self._values["deletion_condition"] = deletion_condition
        if hard_deletion_sync_min_interval_in_seconds is not None:
            self._values["hard_deletion_sync_min_interval_in_seconds"] = hard_deletion_sync_min_interval_in_seconds

    @builtins.property
    def cursor_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.'''
        result = self._values.get("cursor_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deletion_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.'''
        result = self._values.get("deletion_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hard_deletion_sync_min_interval_in_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.'''
        result = self._values.get("hard_deletion_sync_min_interval_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66b7a52353fa3306466481af3ed3c97a9b4ca6413ff1f584f6fabadfeb5016e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCursorColumns")
    def reset_cursor_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCursorColumns", []))

    @jsii.member(jsii_name="resetDeletionCondition")
    def reset_deletion_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionCondition", []))

    @jsii.member(jsii_name="resetHardDeletionSyncMinIntervalInSeconds")
    def reset_hard_deletion_sync_min_interval_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardDeletionSyncMinIntervalInSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="cursorColumnsInput")
    def cursor_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cursorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionConditionInput")
    def deletion_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deletionConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSecondsInput")
    def hard_deletion_sync_min_interval_in_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardDeletionSyncMinIntervalInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="cursorColumns")
    def cursor_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cursorColumns"))

    @cursor_columns.setter
    def cursor_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd609ae7fc8fc682e209eaaaa45bffc9a3cbd46976db6f34eed5cf2cb9e0a94b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cursorColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionCondition")
    def deletion_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletionCondition"))

    @deletion_condition.setter
    def deletion_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fbe7eece88d07a0bd67dc07f4f9bc36811b422d0c3ad1c79ea1ef3c4ba11959)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSeconds")
    def hard_deletion_sync_min_interval_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardDeletionSyncMinIntervalInSeconds"))

    @hard_deletion_sync_min_interval_in_seconds.setter
    def hard_deletion_sync_min_interval_in_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd344f08ae839384697ce74540d9bebdbe62d9b2aee955af34c06d776c4dba70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardDeletionSyncMinIntervalInSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff25d40da20a3f58ea5e51f8c90d47a1ec152d32ac86c30a1df190e839264cd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchema",
    jsii_struct_bases=[],
    name_mapping={
        "destination_catalog": "destinationCatalog",
        "destination_schema": "destinationSchema",
        "source_schema": "sourceSchema",
        "source_catalog": "sourceCatalog",
        "table_configuration": "tableConfiguration",
    },
)
class PipelineIngestionDefinitionObjectsSchema:
    def __init__(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_schema: builtins.str,
        source_catalog: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsSchemaTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        if isinstance(table_configuration, dict):
            table_configuration = PipelineIngestionDefinitionObjectsSchemaTableConfiguration(**table_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fe20da001a233e3a8756b14c8a4c5bfb7f2367387dc5107112e1377a7cd0462)
            check_type(argname="argument destination_catalog", value=destination_catalog, expected_type=type_hints["destination_catalog"])
            check_type(argname="argument destination_schema", value=destination_schema, expected_type=type_hints["destination_schema"])
            check_type(argname="argument source_schema", value=source_schema, expected_type=type_hints["source_schema"])
            check_type(argname="argument source_catalog", value=source_catalog, expected_type=type_hints["source_catalog"])
            check_type(argname="argument table_configuration", value=table_configuration, expected_type=type_hints["table_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination_catalog": destination_catalog,
            "destination_schema": destination_schema,
            "source_schema": source_schema,
        }
        if source_catalog is not None:
            self._values["source_catalog"] = source_catalog
        if table_configuration is not None:
            self._values["table_configuration"] = table_configuration

    @builtins.property
    def destination_catalog(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.'''
        result = self._values.get("destination_catalog")
        assert result is not None, "Required property 'destination_catalog' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.'''
        result = self._values.get("destination_schema")
        assert result is not None, "Required property 'destination_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.'''
        result = self._values.get("source_schema")
        assert result is not None, "Required property 'source_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.'''
        result = self._values.get("source_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_configuration(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfiguration"]:
        '''table_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        result = self._values.get("table_configuration")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsSchema(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsSchemaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchemaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69b6cc34b90f1b782407f1bd7c087dbc9662582fbfb946f7885c5b4402cc5fbf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTableConfiguration")
    def put_table_configuration(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        value = PipelineIngestionDefinitionObjectsSchemaTableConfiguration(
            exclude_columns=exclude_columns,
            include_columns=include_columns,
            primary_keys=primary_keys,
            query_based_connector_config=query_based_connector_config,
            salesforce_include_formula_fields=salesforce_include_formula_fields,
            scd_type=scd_type,
            sequence_by=sequence_by,
        )

        return typing.cast(None, jsii.invoke(self, "putTableConfiguration", [value]))

    @jsii.member(jsii_name="resetSourceCatalog")
    def reset_source_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCatalog", []))

    @jsii.member(jsii_name="resetTableConfiguration")
    def reset_table_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConfiguration", []))

    @builtins.property
    @jsii.member(jsii_name="tableConfiguration")
    def table_configuration(
        self,
    ) -> "PipelineIngestionDefinitionObjectsSchemaTableConfigurationOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsSchemaTableConfigurationOutputReference", jsii.get(self, "tableConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalogInput")
    def destination_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationSchemaInput")
    def destination_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCatalogInput")
    def source_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceSchemaInput")
    def source_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConfigurationInput")
    def table_configuration_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfiguration"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfiguration"], jsii.get(self, "tableConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalog")
    def destination_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationCatalog"))

    @destination_catalog.setter
    def destination_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__166df458d3e3e108e5c8f13f098c782c0dd36d2cf1ef770a60ea61a5cc6ab7e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationSchema")
    def destination_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationSchema"))

    @destination_schema.setter
    def destination_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4222685dc3e0896c806c24c7fea472c740d06bf1bd3c407844507de4d2b9595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCatalog")
    def source_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCatalog"))

    @source_catalog.setter
    def source_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__859b9d014282744993eb944326d222cb9e8876d1e752dab712bb3d7d535061bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceSchema")
    def source_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceSchema"))

    @source_schema.setter
    def source_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc938d897a140918143b6060519c2c82dd1187086c8f384a35ae0d77956580e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsSchema]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsSchema], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsSchema],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3915f38ecf78a782afd41a1b6d39460795cabf8ff616cb27274c9e1188448158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchemaTableConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_columns": "excludeColumns",
        "include_columns": "includeColumns",
        "primary_keys": "primaryKeys",
        "query_based_connector_config": "queryBasedConnectorConfig",
        "salesforce_include_formula_fields": "salesforceIncludeFormulaFields",
        "scd_type": "scdType",
        "sequence_by": "sequenceBy",
    },
)
class PipelineIngestionDefinitionObjectsSchemaTableConfiguration:
    def __init__(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        if isinstance(query_based_connector_config, dict):
            query_based_connector_config = PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig(**query_based_connector_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fcf3e521518df575b9b150372e2548bcf992d0e7f92af77f065e46ba5a2f387)
            check_type(argname="argument exclude_columns", value=exclude_columns, expected_type=type_hints["exclude_columns"])
            check_type(argname="argument include_columns", value=include_columns, expected_type=type_hints["include_columns"])
            check_type(argname="argument primary_keys", value=primary_keys, expected_type=type_hints["primary_keys"])
            check_type(argname="argument query_based_connector_config", value=query_based_connector_config, expected_type=type_hints["query_based_connector_config"])
            check_type(argname="argument salesforce_include_formula_fields", value=salesforce_include_formula_fields, expected_type=type_hints["salesforce_include_formula_fields"])
            check_type(argname="argument scd_type", value=scd_type, expected_type=type_hints["scd_type"])
            check_type(argname="argument sequence_by", value=sequence_by, expected_type=type_hints["sequence_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_columns is not None:
            self._values["exclude_columns"] = exclude_columns
        if include_columns is not None:
            self._values["include_columns"] = include_columns
        if primary_keys is not None:
            self._values["primary_keys"] = primary_keys
        if query_based_connector_config is not None:
            self._values["query_based_connector_config"] = query_based_connector_config
        if salesforce_include_formula_fields is not None:
            self._values["salesforce_include_formula_fields"] = salesforce_include_formula_fields
        if scd_type is not None:
            self._values["scd_type"] = scd_type
        if sequence_by is not None:
            self._values["sequence_by"] = sequence_by

    @builtins.property
    def exclude_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.'''
        result = self._values.get("exclude_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.'''
        result = self._values.get("include_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def primary_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.'''
        result = self._values.get("primary_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_based_connector_config(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig"]:
        '''query_based_connector_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        '''
        result = self._values.get("query_based_connector_config")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig"], result)

    @builtins.property
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.'''
        result = self._values.get("salesforce_include_formula_fields")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def scd_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.'''
        result = self._values.get("scd_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sequence_by(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.'''
        result = self._values.get("sequence_by")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsSchemaTableConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsSchemaTableConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchemaTableConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd089ba50d2270e16c7c62044c5621d697e9c7f11de4ef45a3bafa11e482c453)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putQueryBasedConnectorConfig")
    def put_query_based_connector_config(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        value = PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig(
            cursor_columns=cursor_columns,
            deletion_condition=deletion_condition,
            hard_deletion_sync_min_interval_in_seconds=hard_deletion_sync_min_interval_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putQueryBasedConnectorConfig", [value]))

    @jsii.member(jsii_name="resetExcludeColumns")
    def reset_exclude_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeColumns", []))

    @jsii.member(jsii_name="resetIncludeColumns")
    def reset_include_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeColumns", []))

    @jsii.member(jsii_name="resetPrimaryKeys")
    def reset_primary_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeys", []))

    @jsii.member(jsii_name="resetQueryBasedConnectorConfig")
    def reset_query_based_connector_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryBasedConnectorConfig", []))

    @jsii.member(jsii_name="resetSalesforceIncludeFormulaFields")
    def reset_salesforce_include_formula_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSalesforceIncludeFormulaFields", []))

    @jsii.member(jsii_name="resetScdType")
    def reset_scd_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScdType", []))

    @jsii.member(jsii_name="resetSequenceBy")
    def reset_sequence_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSequenceBy", []))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfig")
    def query_based_connector_config(
        self,
    ) -> "PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfigOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfigOutputReference", jsii.get(self, "queryBasedConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumnsInput")
    def exclude_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeColumnsInput")
    def include_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeysInput")
    def primary_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfigInput")
    def query_based_connector_config_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig"], jsii.get(self, "queryBasedConnectorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFieldsInput")
    def salesforce_include_formula_fields_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "salesforceIncludeFormulaFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="scdTypeInput")
    def scd_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scdTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sequenceByInput")
    def sequence_by_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sequenceByInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumns")
    def exclude_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeColumns"))

    @exclude_columns.setter
    def exclude_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25408907137cfa926475507824c9998d7292682ef12e9251b1d7943309df5236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeColumns")
    def include_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeColumns"))

    @include_columns.setter
    def include_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a0d11f22edc84413508431d68c111bd7ce27367d321987c2bc0a624fafed4c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeys")
    def primary_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeys"))

    @primary_keys.setter
    def primary_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135457dcdb8e7279bd6fec6aac1b0025cdce30d96b75babe0be75563ed677d1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFields")
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "salesforceIncludeFormulaFields"))

    @salesforce_include_formula_fields.setter
    def salesforce_include_formula_fields(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b92212d2fb8f06398e84258ecf0fbd3e6f37d32dcf71aa668b1eff96ab7212b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "salesforceIncludeFormulaFields", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scdType")
    def scd_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scdType"))

    @scd_type.setter
    def scd_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36bb9d050ab634dfa52ed9bed774bce23dc50a0467a3361780eca51d09c3c6fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scdType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequenceBy")
    def sequence_by(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sequenceBy"))

    @sequence_by.setter
    def sequence_by(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3afe8917b117ffe1c320819f5c5917ba165c70dbfa617b6f3107ebe397e7e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequenceBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfiguration]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8a5ef3b233c9c68c0d07ab14db0b0ad42d6c452472b373e55f3e3f1910eb60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cursor_columns": "cursorColumns",
        "deletion_condition": "deletionCondition",
        "hard_deletion_sync_min_interval_in_seconds": "hardDeletionSyncMinIntervalInSeconds",
    },
)
class PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig:
    def __init__(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296b9cf1b2a31c16d55935e577fe59245a9e11a5fb337afb5533f5c0b0e22def)
            check_type(argname="argument cursor_columns", value=cursor_columns, expected_type=type_hints["cursor_columns"])
            check_type(argname="argument deletion_condition", value=deletion_condition, expected_type=type_hints["deletion_condition"])
            check_type(argname="argument hard_deletion_sync_min_interval_in_seconds", value=hard_deletion_sync_min_interval_in_seconds, expected_type=type_hints["hard_deletion_sync_min_interval_in_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cursor_columns is not None:
            self._values["cursor_columns"] = cursor_columns
        if deletion_condition is not None:
            self._values["deletion_condition"] = deletion_condition
        if hard_deletion_sync_min_interval_in_seconds is not None:
            self._values["hard_deletion_sync_min_interval_in_seconds"] = hard_deletion_sync_min_interval_in_seconds

    @builtins.property
    def cursor_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.'''
        result = self._values.get("cursor_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deletion_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.'''
        result = self._values.get("deletion_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hard_deletion_sync_min_interval_in_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.'''
        result = self._values.get("hard_deletion_sync_min_interval_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f89cba9bf9f5c9ccde116037836e8c8a2a80d9d9822aac65f143c4b11aa4d39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCursorColumns")
    def reset_cursor_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCursorColumns", []))

    @jsii.member(jsii_name="resetDeletionCondition")
    def reset_deletion_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionCondition", []))

    @jsii.member(jsii_name="resetHardDeletionSyncMinIntervalInSeconds")
    def reset_hard_deletion_sync_min_interval_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardDeletionSyncMinIntervalInSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="cursorColumnsInput")
    def cursor_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cursorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionConditionInput")
    def deletion_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deletionConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSecondsInput")
    def hard_deletion_sync_min_interval_in_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardDeletionSyncMinIntervalInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="cursorColumns")
    def cursor_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cursorColumns"))

    @cursor_columns.setter
    def cursor_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ab98bb6ce2c1f2192fe451a438aea77f716c957f406a54e846570e328f26a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cursorColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionCondition")
    def deletion_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletionCondition"))

    @deletion_condition.setter
    def deletion_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6675002bfff6d8b054478147e8f1bc6bd17a52e2410f60e5a1e6b6a0925fdbf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSeconds")
    def hard_deletion_sync_min_interval_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardDeletionSyncMinIntervalInSeconds"))

    @hard_deletion_sync_min_interval_in_seconds.setter
    def hard_deletion_sync_min_interval_in_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07552a408da7cd70d7e806728d7936314af1da0430a021c947c9cda6e3cf11d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardDeletionSyncMinIntervalInSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e40aaed1140283544c9f8caf7f33fb6dc7e7c76e3a25162a3d7dd4edde2053eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTable",
    jsii_struct_bases=[],
    name_mapping={
        "destination_catalog": "destinationCatalog",
        "destination_schema": "destinationSchema",
        "source_table": "sourceTable",
        "destination_table": "destinationTable",
        "source_catalog": "sourceCatalog",
        "source_schema": "sourceSchema",
        "table_configuration": "tableConfiguration",
    },
)
class PipelineIngestionDefinitionObjectsTable:
    def __init__(
        self,
        *,
        destination_catalog: builtins.str,
        destination_schema: builtins.str,
        source_table: builtins.str,
        destination_table: typing.Optional[builtins.str] = None,
        source_catalog: typing.Optional[builtins.str] = None,
        source_schema: typing.Optional[builtins.str] = None,
        table_configuration: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsTableTableConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.
        :param destination_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.
        :param source_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_table Pipeline#source_table}.
        :param destination_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        :param source_schema: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.
        :param table_configuration: table_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        if isinstance(table_configuration, dict):
            table_configuration = PipelineIngestionDefinitionObjectsTableTableConfiguration(**table_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41170ca88768dfdba38616c64eab02a05ad0c69e72f3378af4ab3cc71db2f2f4)
            check_type(argname="argument destination_catalog", value=destination_catalog, expected_type=type_hints["destination_catalog"])
            check_type(argname="argument destination_schema", value=destination_schema, expected_type=type_hints["destination_schema"])
            check_type(argname="argument source_table", value=source_table, expected_type=type_hints["source_table"])
            check_type(argname="argument destination_table", value=destination_table, expected_type=type_hints["destination_table"])
            check_type(argname="argument source_catalog", value=source_catalog, expected_type=type_hints["source_catalog"])
            check_type(argname="argument source_schema", value=source_schema, expected_type=type_hints["source_schema"])
            check_type(argname="argument table_configuration", value=table_configuration, expected_type=type_hints["table_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination_catalog": destination_catalog,
            "destination_schema": destination_schema,
            "source_table": source_table,
        }
        if destination_table is not None:
            self._values["destination_table"] = destination_table
        if source_catalog is not None:
            self._values["source_catalog"] = source_catalog
        if source_schema is not None:
            self._values["source_schema"] = source_schema
        if table_configuration is not None:
            self._values["table_configuration"] = table_configuration

    @builtins.property
    def destination_catalog(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_catalog Pipeline#destination_catalog}.'''
        result = self._values.get("destination_catalog")
        assert result is not None, "Required property 'destination_catalog' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_schema(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_schema Pipeline#destination_schema}.'''
        result = self._values.get("destination_schema")
        assert result is not None, "Required property 'destination_schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_table(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_table Pipeline#source_table}.'''
        result = self._values.get("source_table")
        assert result is not None, "Required property 'source_table' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_table(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#destination_table Pipeline#destination_table}.'''
        result = self._values.get("destination_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.'''
        result = self._values.get("source_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_schema Pipeline#source_schema}.'''
        result = self._values.get("source_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_configuration(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfiguration"]:
        '''table_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#table_configuration Pipeline#table_configuration}
        '''
        result = self._values.get("table_configuration")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsTable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsTableOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTableOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab453a20e815d0c840141b1a26a427331132f583ba986ec34070c31de4dfc048)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTableConfiguration")
    def put_table_configuration(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        value = PipelineIngestionDefinitionObjectsTableTableConfiguration(
            exclude_columns=exclude_columns,
            include_columns=include_columns,
            primary_keys=primary_keys,
            query_based_connector_config=query_based_connector_config,
            salesforce_include_formula_fields=salesforce_include_formula_fields,
            scd_type=scd_type,
            sequence_by=sequence_by,
        )

        return typing.cast(None, jsii.invoke(self, "putTableConfiguration", [value]))

    @jsii.member(jsii_name="resetDestinationTable")
    def reset_destination_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationTable", []))

    @jsii.member(jsii_name="resetSourceCatalog")
    def reset_source_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCatalog", []))

    @jsii.member(jsii_name="resetSourceSchema")
    def reset_source_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceSchema", []))

    @jsii.member(jsii_name="resetTableConfiguration")
    def reset_table_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConfiguration", []))

    @builtins.property
    @jsii.member(jsii_name="tableConfiguration")
    def table_configuration(
        self,
    ) -> "PipelineIngestionDefinitionObjectsTableTableConfigurationOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsTableTableConfigurationOutputReference", jsii.get(self, "tableConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalogInput")
    def destination_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationSchemaInput")
    def destination_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationTableInput")
    def destination_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationTableInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCatalogInput")
    def source_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceSchemaInput")
    def source_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTableInput")
    def source_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTableInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConfigurationInput")
    def table_configuration_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfiguration"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfiguration"], jsii.get(self, "tableConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationCatalog")
    def destination_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationCatalog"))

    @destination_catalog.setter
    def destination_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c6a07bff158bdf73aadeefce07a22e813b5ca53cbf528b3fd9d96774e2fba6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationSchema")
    def destination_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationSchema"))

    @destination_schema.setter
    def destination_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187de915cd3b0e84ed631cf79806f114c272c753dcb5455e7aeb0fbb1544dde1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationTable")
    def destination_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationTable"))

    @destination_table.setter
    def destination_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a33667d9c4524627c26d26590637d56be8330788a91987efd95ce222a8c4a7d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCatalog")
    def source_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCatalog"))

    @source_catalog.setter
    def source_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d6dc3baa2cf15eda1457f434cf46547bf8cadc0398c8203c7303a25f35c2f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceSchema")
    def source_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceSchema"))

    @source_schema.setter
    def source_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf296f1abe222661e4a2d027a55a5c7e2e0b4db22e288fcca1162d0270238dc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceTable")
    def source_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceTable"))

    @source_table.setter
    def source_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78d026e1b50dca8dd6f362a47ca6297e30ff9354d8e2ef23acee6559e5ac7023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsTable]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsTable], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsTable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6eb1308f00a94b49033cea6615bdab9ef0e5d90145c6546d872c24349d00d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTableTableConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_columns": "excludeColumns",
        "include_columns": "includeColumns",
        "primary_keys": "primaryKeys",
        "query_based_connector_config": "queryBasedConnectorConfig",
        "salesforce_include_formula_fields": "salesforceIncludeFormulaFields",
        "scd_type": "scdType",
        "sequence_by": "sequenceBy",
    },
)
class PipelineIngestionDefinitionObjectsTableTableConfiguration:
    def __init__(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        if isinstance(query_based_connector_config, dict):
            query_based_connector_config = PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig(**query_based_connector_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f3f8af5ec97a7ec34117bd984ed510996aa072861e70bacebfb046379de3fbb)
            check_type(argname="argument exclude_columns", value=exclude_columns, expected_type=type_hints["exclude_columns"])
            check_type(argname="argument include_columns", value=include_columns, expected_type=type_hints["include_columns"])
            check_type(argname="argument primary_keys", value=primary_keys, expected_type=type_hints["primary_keys"])
            check_type(argname="argument query_based_connector_config", value=query_based_connector_config, expected_type=type_hints["query_based_connector_config"])
            check_type(argname="argument salesforce_include_formula_fields", value=salesforce_include_formula_fields, expected_type=type_hints["salesforce_include_formula_fields"])
            check_type(argname="argument scd_type", value=scd_type, expected_type=type_hints["scd_type"])
            check_type(argname="argument sequence_by", value=sequence_by, expected_type=type_hints["sequence_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_columns is not None:
            self._values["exclude_columns"] = exclude_columns
        if include_columns is not None:
            self._values["include_columns"] = include_columns
        if primary_keys is not None:
            self._values["primary_keys"] = primary_keys
        if query_based_connector_config is not None:
            self._values["query_based_connector_config"] = query_based_connector_config
        if salesforce_include_formula_fields is not None:
            self._values["salesforce_include_formula_fields"] = salesforce_include_formula_fields
        if scd_type is not None:
            self._values["scd_type"] = scd_type
        if sequence_by is not None:
            self._values["sequence_by"] = sequence_by

    @builtins.property
    def exclude_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.'''
        result = self._values.get("exclude_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.'''
        result = self._values.get("include_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def primary_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.'''
        result = self._values.get("primary_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_based_connector_config(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig"]:
        '''query_based_connector_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        '''
        result = self._values.get("query_based_connector_config")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig"], result)

    @builtins.property
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.'''
        result = self._values.get("salesforce_include_formula_fields")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def scd_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.'''
        result = self._values.get("scd_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sequence_by(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.'''
        result = self._values.get("sequence_by")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsTableTableConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsTableTableConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTableTableConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60c14783407d6ff9e3e94e7c463e5aaa88660d4dd13e2366fc35a9d4eef920a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putQueryBasedConnectorConfig")
    def put_query_based_connector_config(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        value = PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig(
            cursor_columns=cursor_columns,
            deletion_condition=deletion_condition,
            hard_deletion_sync_min_interval_in_seconds=hard_deletion_sync_min_interval_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putQueryBasedConnectorConfig", [value]))

    @jsii.member(jsii_name="resetExcludeColumns")
    def reset_exclude_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeColumns", []))

    @jsii.member(jsii_name="resetIncludeColumns")
    def reset_include_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeColumns", []))

    @jsii.member(jsii_name="resetPrimaryKeys")
    def reset_primary_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeys", []))

    @jsii.member(jsii_name="resetQueryBasedConnectorConfig")
    def reset_query_based_connector_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryBasedConnectorConfig", []))

    @jsii.member(jsii_name="resetSalesforceIncludeFormulaFields")
    def reset_salesforce_include_formula_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSalesforceIncludeFormulaFields", []))

    @jsii.member(jsii_name="resetScdType")
    def reset_scd_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScdType", []))

    @jsii.member(jsii_name="resetSequenceBy")
    def reset_sequence_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSequenceBy", []))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfig")
    def query_based_connector_config(
        self,
    ) -> "PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfigOutputReference":
        return typing.cast("PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfigOutputReference", jsii.get(self, "queryBasedConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumnsInput")
    def exclude_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeColumnsInput")
    def include_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeysInput")
    def primary_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfigInput")
    def query_based_connector_config_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig"], jsii.get(self, "queryBasedConnectorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFieldsInput")
    def salesforce_include_formula_fields_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "salesforceIncludeFormulaFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="scdTypeInput")
    def scd_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scdTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sequenceByInput")
    def sequence_by_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sequenceByInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumns")
    def exclude_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeColumns"))

    @exclude_columns.setter
    def exclude_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40e93fea143d8c0f054b208d4f7367a4549a9c9ea35d706e2bbe20ec84d7ef55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeColumns")
    def include_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeColumns"))

    @include_columns.setter
    def include_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0166ca2f47d0c918ae84f69ae907a89847647219ff33a325246882916f21487c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeys")
    def primary_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeys"))

    @primary_keys.setter
    def primary_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8031a5f88964aadd82e92db61ca0f5159360dedc779338c2e35c59c08345768c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFields")
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "salesforceIncludeFormulaFields"))

    @salesforce_include_formula_fields.setter
    def salesforce_include_formula_fields(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7a5ea75cb58414c7f9a9fb1d0bb4e01d9811188231d8f9e52dc16b0338bf18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "salesforceIncludeFormulaFields", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scdType")
    def scd_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scdType"))

    @scd_type.setter
    def scd_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddac130d835315919e4341ac75f4ed1a66fa6d31eedc071153c296fda26061f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scdType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequenceBy")
    def sequence_by(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sequenceBy"))

    @sequence_by.setter
    def sequence_by(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3513bbf0f7d3e5c7b214b9b5edd2ce11262cf686a1c2980c20b96670a11cc980)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequenceBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfiguration]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d335360687b4ab8d4316098cfa1aa20a6a0f11ce6e38699ef40670848aa5534f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cursor_columns": "cursorColumns",
        "deletion_condition": "deletionCondition",
        "hard_deletion_sync_min_interval_in_seconds": "hardDeletionSyncMinIntervalInSeconds",
    },
)
class PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig:
    def __init__(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be35be9b12dccdc8bd6b1ad5d15fb46ba2c7fe961ce9159afc07a63ece579e2)
            check_type(argname="argument cursor_columns", value=cursor_columns, expected_type=type_hints["cursor_columns"])
            check_type(argname="argument deletion_condition", value=deletion_condition, expected_type=type_hints["deletion_condition"])
            check_type(argname="argument hard_deletion_sync_min_interval_in_seconds", value=hard_deletion_sync_min_interval_in_seconds, expected_type=type_hints["hard_deletion_sync_min_interval_in_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cursor_columns is not None:
            self._values["cursor_columns"] = cursor_columns
        if deletion_condition is not None:
            self._values["deletion_condition"] = deletion_condition
        if hard_deletion_sync_min_interval_in_seconds is not None:
            self._values["hard_deletion_sync_min_interval_in_seconds"] = hard_deletion_sync_min_interval_in_seconds

    @builtins.property
    def cursor_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.'''
        result = self._values.get("cursor_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deletion_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.'''
        result = self._values.get("deletion_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hard_deletion_sync_min_interval_in_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.'''
        result = self._values.get("hard_deletion_sync_min_interval_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f74725d58f1f1200f95dd99cc67980c23d659dc0823409ad2816bed17c2d0f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCursorColumns")
    def reset_cursor_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCursorColumns", []))

    @jsii.member(jsii_name="resetDeletionCondition")
    def reset_deletion_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionCondition", []))

    @jsii.member(jsii_name="resetHardDeletionSyncMinIntervalInSeconds")
    def reset_hard_deletion_sync_min_interval_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardDeletionSyncMinIntervalInSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="cursorColumnsInput")
    def cursor_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cursorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionConditionInput")
    def deletion_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deletionConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSecondsInput")
    def hard_deletion_sync_min_interval_in_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardDeletionSyncMinIntervalInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="cursorColumns")
    def cursor_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cursorColumns"))

    @cursor_columns.setter
    def cursor_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8619547a6d03daec320c988791150abb368ca32abf72cb3f1eefb8f5255fb7f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cursorColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionCondition")
    def deletion_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletionCondition"))

    @deletion_condition.setter
    def deletion_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f48d1308d12285b1a81adc4eaae1fdcdd0e4a83c78824d9e151e50e4182dafc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSeconds")
    def hard_deletion_sync_min_interval_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardDeletionSyncMinIntervalInSeconds"))

    @hard_deletion_sync_min_interval_in_seconds.setter
    def hard_deletion_sync_min_interval_in_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4683bc644624250dcec5d5254cf690fbbf0ce17af339307477962078bf993257)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardDeletionSyncMinIntervalInSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3658ac6add6bfdc47fb10c708e9e63ca04d74fc15802ff1da6fe84406ec1627d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineIngestionDefinitionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c390900a16391ecf82e8f1c1b0e0d73ffbb21fd66ab90b52492b72dd10fd54bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putObjects")
    def put_objects(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineIngestionDefinitionObjects, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c89b6db6167bd191775e820a6421e12c555eaa68afd0a34bfbd110b59c3346dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putObjects", [value]))

    @jsii.member(jsii_name="putSourceConfigurations")
    def put_source_configurations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PipelineIngestionDefinitionSourceConfigurations", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__417a3b4089c58d12309ffea6fbb1e389a7496fab625ee9f8ca208e3f2fb54937)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSourceConfigurations", [value]))

    @jsii.member(jsii_name="putTableConfiguration")
    def put_table_configuration(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        value = PipelineIngestionDefinitionTableConfiguration(
            exclude_columns=exclude_columns,
            include_columns=include_columns,
            primary_keys=primary_keys,
            query_based_connector_config=query_based_connector_config,
            salesforce_include_formula_fields=salesforce_include_formula_fields,
            scd_type=scd_type,
            sequence_by=sequence_by,
        )

        return typing.cast(None, jsii.invoke(self, "putTableConfiguration", [value]))

    @jsii.member(jsii_name="resetConnectionName")
    def reset_connection_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionName", []))

    @jsii.member(jsii_name="resetIngestionGatewayId")
    def reset_ingestion_gateway_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngestionGatewayId", []))

    @jsii.member(jsii_name="resetObjects")
    def reset_objects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjects", []))

    @jsii.member(jsii_name="resetSourceConfigurations")
    def reset_source_configurations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceConfigurations", []))

    @jsii.member(jsii_name="resetSourceType")
    def reset_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceType", []))

    @jsii.member(jsii_name="resetTableConfiguration")
    def reset_table_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableConfiguration", []))

    @builtins.property
    @jsii.member(jsii_name="objects")
    def objects(self) -> PipelineIngestionDefinitionObjectsList:
        return typing.cast(PipelineIngestionDefinitionObjectsList, jsii.get(self, "objects"))

    @builtins.property
    @jsii.member(jsii_name="sourceConfigurations")
    def source_configurations(
        self,
    ) -> "PipelineIngestionDefinitionSourceConfigurationsList":
        return typing.cast("PipelineIngestionDefinitionSourceConfigurationsList", jsii.get(self, "sourceConfigurations"))

    @builtins.property
    @jsii.member(jsii_name="tableConfiguration")
    def table_configuration(
        self,
    ) -> "PipelineIngestionDefinitionTableConfigurationOutputReference":
        return typing.cast("PipelineIngestionDefinitionTableConfigurationOutputReference", jsii.get(self, "tableConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="connectionNameInput")
    def connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ingestionGatewayIdInput")
    def ingestion_gateway_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ingestionGatewayIdInput"))

    @builtins.property
    @jsii.member(jsii_name="objectsInput")
    def objects_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]], jsii.get(self, "objectsInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceConfigurationsInput")
    def source_configurations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionSourceConfigurations"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PipelineIngestionDefinitionSourceConfigurations"]]], jsii.get(self, "sourceConfigurationsInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTypeInput")
    def source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tableConfigurationInput")
    def table_configuration_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionTableConfiguration"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionTableConfiguration"], jsii.get(self, "tableConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ae1f384733d20a9e8d0703916c34185e19cfea0987aaf02ced0124881894399)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingestionGatewayId")
    def ingestion_gateway_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ingestionGatewayId"))

    @ingestion_gateway_id.setter
    def ingestion_gateway_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5476e64786101bb6cb7caaceec5dda14b7250ce30cf30b66812f46d8e94f6200)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingestionGatewayId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01c20f5c899556d70f3980cb1345155e7b8f9706f773f1113a57daf295f0379b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineIngestionDefinition]:
        return typing.cast(typing.Optional[PipelineIngestionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4583a74d96f1c18f22b33ff17c9b114efdaea3898d7c7f126ed328bec9069f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurations",
    jsii_struct_bases=[],
    name_mapping={"catalog": "catalog"},
)
class PipelineIngestionDefinitionSourceConfigurations:
    def __init__(
        self,
        *,
        catalog: typing.Optional[typing.Union["PipelineIngestionDefinitionSourceConfigurationsCatalog", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param catalog: catalog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}
        '''
        if isinstance(catalog, dict):
            catalog = PipelineIngestionDefinitionSourceConfigurationsCatalog(**catalog)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b148d879e110577523487452fbe5744c5746698c26c7ce1095cc368f3600f28c)
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if catalog is not None:
            self._values["catalog"] = catalog

    @builtins.property
    def catalog(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalog"]:
        '''catalog block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#catalog Pipeline#catalog}
        '''
        result = self._values.get("catalog")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalog"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionSourceConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalog",
    jsii_struct_bases=[],
    name_mapping={"postgres": "postgres", "source_catalog": "sourceCatalog"},
)
class PipelineIngestionDefinitionSourceConfigurationsCatalog:
    def __init__(
        self,
        *,
        postgres: typing.Optional[typing.Union["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres", typing.Dict[builtins.str, typing.Any]]] = None,
        source_catalog: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param postgres: postgres block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#postgres Pipeline#postgres}
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        '''
        if isinstance(postgres, dict):
            postgres = PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres(**postgres)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__087bf8c8f4d2e8c89ea335992b6dd2e3a3d9d99bd1ea065071be7ff0a5ec629d)
            check_type(argname="argument postgres", value=postgres, expected_type=type_hints["postgres"])
            check_type(argname="argument source_catalog", value=source_catalog, expected_type=type_hints["source_catalog"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if postgres is not None:
            self._values["postgres"] = postgres
        if source_catalog is not None:
            self._values["source_catalog"] = source_catalog

    @builtins.property
    def postgres(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres"]:
        '''postgres block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#postgres Pipeline#postgres}
        '''
        result = self._values.get("postgres")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres"], result)

    @builtins.property
    def source_catalog(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.'''
        result = self._values.get("source_catalog")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionSourceConfigurationsCatalog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionSourceConfigurationsCatalogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca7d03bb9f9d707168800a509389dd7361117b219da952f6a3363276ac785c55)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPostgres")
    def put_postgres(
        self,
        *,
        slot_config: typing.Optional[typing.Union["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param slot_config: slot_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_config Pipeline#slot_config}
        '''
        value = PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres(
            slot_config=slot_config
        )

        return typing.cast(None, jsii.invoke(self, "putPostgres", [value]))

    @jsii.member(jsii_name="resetPostgres")
    def reset_postgres(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgres", []))

    @jsii.member(jsii_name="resetSourceCatalog")
    def reset_source_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCatalog", []))

    @builtins.property
    @jsii.member(jsii_name="postgres")
    def postgres(
        self,
    ) -> "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresOutputReference":
        return typing.cast("PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresOutputReference", jsii.get(self, "postgres"))

    @builtins.property
    @jsii.member(jsii_name="postgresInput")
    def postgres_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres"], jsii.get(self, "postgresInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCatalogInput")
    def source_catalog_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCatalogInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCatalog")
    def source_catalog(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCatalog"))

    @source_catalog.setter
    def source_catalog(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b68df714e611a493a84d849f0a2659568ee556ed2dc37590220cda884857140b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCatalog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__767fe44d037f5dabc5706011f1e4ffb86d2a5de88176e060d4f30b42d772ef93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres",
    jsii_struct_bases=[],
    name_mapping={"slot_config": "slotConfig"},
)
class PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres:
    def __init__(
        self,
        *,
        slot_config: typing.Optional[typing.Union["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param slot_config: slot_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_config Pipeline#slot_config}
        '''
        if isinstance(slot_config, dict):
            slot_config = PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig(**slot_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad81892acff8d987eafc1de2e13c03142b66d10aaad20247afeee353f3e6cbc)
            check_type(argname="argument slot_config", value=slot_config, expected_type=type_hints["slot_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if slot_config is not None:
            self._values["slot_config"] = slot_config

    @builtins.property
    def slot_config(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig"]:
        '''slot_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_config Pipeline#slot_config}
        '''
        result = self._values.get("slot_config")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffdb494680107f7a9d8268f128cca53a6636192142c4635436ad4625c3696767)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSlotConfig")
    def put_slot_config(
        self,
        *,
        publication_name: typing.Optional[builtins.str] = None,
        slot_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param publication_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#publication_name Pipeline#publication_name}.
        :param slot_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_name Pipeline#slot_name}.
        '''
        value = PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig(
            publication_name=publication_name, slot_name=slot_name
        )

        return typing.cast(None, jsii.invoke(self, "putSlotConfig", [value]))

    @jsii.member(jsii_name="resetSlotConfig")
    def reset_slot_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlotConfig", []))

    @builtins.property
    @jsii.member(jsii_name="slotConfig")
    def slot_config(
        self,
    ) -> "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfigOutputReference":
        return typing.cast("PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfigOutputReference", jsii.get(self, "slotConfig"))

    @builtins.property
    @jsii.member(jsii_name="slotConfigInput")
    def slot_config_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig"], jsii.get(self, "slotConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1554139a74c7bfaf4c7140c015425bb9e82bbebee34957dab960797458e750e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig",
    jsii_struct_bases=[],
    name_mapping={"publication_name": "publicationName", "slot_name": "slotName"},
)
class PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig:
    def __init__(
        self,
        *,
        publication_name: typing.Optional[builtins.str] = None,
        slot_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param publication_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#publication_name Pipeline#publication_name}.
        :param slot_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_name Pipeline#slot_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__019e7ab6182fd2c9605b97d9ab29d06c8946e8d2a157330d1ef28b78ac6a9a8f)
            check_type(argname="argument publication_name", value=publication_name, expected_type=type_hints["publication_name"])
            check_type(argname="argument slot_name", value=slot_name, expected_type=type_hints["slot_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if publication_name is not None:
            self._values["publication_name"] = publication_name
        if slot_name is not None:
            self._values["slot_name"] = slot_name

    @builtins.property
    def publication_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#publication_name Pipeline#publication_name}.'''
        result = self._values.get("publication_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def slot_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#slot_name Pipeline#slot_name}.'''
        result = self._values.get("slot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__648832be68b3cb80429f6812b4769cae59351988601de7dc13a3a7a79267c57b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPublicationName")
    def reset_publication_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicationName", []))

    @jsii.member(jsii_name="resetSlotName")
    def reset_slot_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlotName", []))

    @builtins.property
    @jsii.member(jsii_name="publicationNameInput")
    def publication_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicationNameInput"))

    @builtins.property
    @jsii.member(jsii_name="slotNameInput")
    def slot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "slotNameInput"))

    @builtins.property
    @jsii.member(jsii_name="publicationName")
    def publication_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicationName"))

    @publication_name.setter
    def publication_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4316d5a05a6956b944474d8a63e344987f37f08eb69d58632500205abb5afd59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicationName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slotName")
    def slot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slotName"))

    @slot_name.setter
    def slot_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c61f139de71b86272307e382a54bd22a127e391c0dcfb86f2c1a4b3fa3f1aa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slotName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8803c7987bfea8ada46e49e35a4fa8c228f078b10811501e760382ac77a741d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineIngestionDefinitionSourceConfigurationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__936b98b40514dc1ce2561a4632222043304cd4ffb2818b777e05df3e81a591ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PipelineIngestionDefinitionSourceConfigurationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__733d71c11dd2926dc5cae8ed7248cc1abc70353b828696f190dc1b6aee88632d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineIngestionDefinitionSourceConfigurationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ce134b945d30c4e632603a7f8fa52a04db532ccff74738a297376bf69185cd5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b018fb30c77f9f947fe192f2a6eb5449a5402e177ee268171608d62d28ae00be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2a0910b832b429670694c9216c21acf76154d52bef7cce1d3ab05962717c793a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionSourceConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionSourceConfigurations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionSourceConfigurations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__967d7b7538fb9aaa9bc4ec918f308dec0292f0a29025bf2218932722a96ca25e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineIngestionDefinitionSourceConfigurationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionSourceConfigurationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bf290952e2e3d8d073bd1ce533f03d305e3572fbb845e60ab0ee4899bc6b9de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCatalog")
    def put_catalog(
        self,
        *,
        postgres: typing.Optional[typing.Union[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres, typing.Dict[builtins.str, typing.Any]]] = None,
        source_catalog: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param postgres: postgres block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#postgres Pipeline#postgres}
        :param source_catalog: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#source_catalog Pipeline#source_catalog}.
        '''
        value = PipelineIngestionDefinitionSourceConfigurationsCatalog(
            postgres=postgres, source_catalog=source_catalog
        )

        return typing.cast(None, jsii.invoke(self, "putCatalog", [value]))

    @jsii.member(jsii_name="resetCatalog")
    def reset_catalog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCatalog", []))

    @builtins.property
    @jsii.member(jsii_name="catalog")
    def catalog(
        self,
    ) -> PipelineIngestionDefinitionSourceConfigurationsCatalogOutputReference:
        return typing.cast(PipelineIngestionDefinitionSourceConfigurationsCatalogOutputReference, jsii.get(self, "catalog"))

    @builtins.property
    @jsii.member(jsii_name="catalogInput")
    def catalog_input(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog], jsii.get(self, "catalogInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionSourceConfigurations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionSourceConfigurations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionSourceConfigurations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4503d4875e92373d8c3dd03f954651574d43ba86a96d840063a8e5aebba5a36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionTableConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_columns": "excludeColumns",
        "include_columns": "includeColumns",
        "primary_keys": "primaryKeys",
        "query_based_connector_config": "queryBasedConnectorConfig",
        "salesforce_include_formula_fields": "salesforceIncludeFormulaFields",
        "scd_type": "scdType",
        "sequence_by": "sequenceBy",
    },
)
class PipelineIngestionDefinitionTableConfiguration:
    def __init__(
        self,
        *,
        exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_based_connector_config: typing.Optional[typing.Union["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        scd_type: typing.Optional[builtins.str] = None,
        sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param exclude_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.
        :param include_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.
        :param primary_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.
        :param query_based_connector_config: query_based_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        :param salesforce_include_formula_fields: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.
        :param scd_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.
        :param sequence_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.
        '''
        if isinstance(query_based_connector_config, dict):
            query_based_connector_config = PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig(**query_based_connector_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79880d315425bc50cc65ac0ae6f469045fbb3b6259a93a1cd6a4b5e3ab3f4f3f)
            check_type(argname="argument exclude_columns", value=exclude_columns, expected_type=type_hints["exclude_columns"])
            check_type(argname="argument include_columns", value=include_columns, expected_type=type_hints["include_columns"])
            check_type(argname="argument primary_keys", value=primary_keys, expected_type=type_hints["primary_keys"])
            check_type(argname="argument query_based_connector_config", value=query_based_connector_config, expected_type=type_hints["query_based_connector_config"])
            check_type(argname="argument salesforce_include_formula_fields", value=salesforce_include_formula_fields, expected_type=type_hints["salesforce_include_formula_fields"])
            check_type(argname="argument scd_type", value=scd_type, expected_type=type_hints["scd_type"])
            check_type(argname="argument sequence_by", value=sequence_by, expected_type=type_hints["sequence_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_columns is not None:
            self._values["exclude_columns"] = exclude_columns
        if include_columns is not None:
            self._values["include_columns"] = include_columns
        if primary_keys is not None:
            self._values["primary_keys"] = primary_keys
        if query_based_connector_config is not None:
            self._values["query_based_connector_config"] = query_based_connector_config
        if salesforce_include_formula_fields is not None:
            self._values["salesforce_include_formula_fields"] = salesforce_include_formula_fields
        if scd_type is not None:
            self._values["scd_type"] = scd_type
        if sequence_by is not None:
            self._values["sequence_by"] = sequence_by

    @builtins.property
    def exclude_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclude_columns Pipeline#exclude_columns}.'''
        result = self._values.get("exclude_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include_columns Pipeline#include_columns}.'''
        result = self._values.get("include_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def primary_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#primary_keys Pipeline#primary_keys}.'''
        result = self._values.get("primary_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_based_connector_config(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig"]:
        '''query_based_connector_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#query_based_connector_config Pipeline#query_based_connector_config}
        '''
        result = self._values.get("query_based_connector_config")
        return typing.cast(typing.Optional["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig"], result)

    @builtins.property
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#salesforce_include_formula_fields Pipeline#salesforce_include_formula_fields}.'''
        result = self._values.get("salesforce_include_formula_fields")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def scd_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#scd_type Pipeline#scd_type}.'''
        result = self._values.get("scd_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sequence_by(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#sequence_by Pipeline#sequence_by}.'''
        result = self._values.get("sequence_by")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionTableConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionTableConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionTableConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d04b1380d31ab94e68427dbf5cb9b5727a8f988d41b1e1fb73763e7da95f0ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putQueryBasedConnectorConfig")
    def put_query_based_connector_config(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        value = PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig(
            cursor_columns=cursor_columns,
            deletion_condition=deletion_condition,
            hard_deletion_sync_min_interval_in_seconds=hard_deletion_sync_min_interval_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putQueryBasedConnectorConfig", [value]))

    @jsii.member(jsii_name="resetExcludeColumns")
    def reset_exclude_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeColumns", []))

    @jsii.member(jsii_name="resetIncludeColumns")
    def reset_include_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeColumns", []))

    @jsii.member(jsii_name="resetPrimaryKeys")
    def reset_primary_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryKeys", []))

    @jsii.member(jsii_name="resetQueryBasedConnectorConfig")
    def reset_query_based_connector_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryBasedConnectorConfig", []))

    @jsii.member(jsii_name="resetSalesforceIncludeFormulaFields")
    def reset_salesforce_include_formula_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSalesforceIncludeFormulaFields", []))

    @jsii.member(jsii_name="resetScdType")
    def reset_scd_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScdType", []))

    @jsii.member(jsii_name="resetSequenceBy")
    def reset_sequence_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSequenceBy", []))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfig")
    def query_based_connector_config(
        self,
    ) -> "PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfigOutputReference":
        return typing.cast("PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfigOutputReference", jsii.get(self, "queryBasedConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumnsInput")
    def exclude_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="includeColumnsInput")
    def include_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryKeysInput")
    def primary_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "primaryKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="queryBasedConnectorConfigInput")
    def query_based_connector_config_input(
        self,
    ) -> typing.Optional["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig"]:
        return typing.cast(typing.Optional["PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig"], jsii.get(self, "queryBasedConnectorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFieldsInput")
    def salesforce_include_formula_fields_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "salesforceIncludeFormulaFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="scdTypeInput")
    def scd_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scdTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sequenceByInput")
    def sequence_by_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sequenceByInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeColumns")
    def exclude_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeColumns"))

    @exclude_columns.setter
    def exclude_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eee803e975a786c79c28b9960a593a1a6a24e915e5e4bd4df0170e885d79c0a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeColumns")
    def include_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeColumns"))

    @include_columns.setter
    def include_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bab630325de7ecfc139867673898c80d9c061bc356f743436b3d53eba36725c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryKeys")
    def primary_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "primaryKeys"))

    @primary_keys.setter
    def primary_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a1fe7bed1f8d6fed4284a92c0c50cb33266e75caa4da6cf8f0545da142d8ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="salesforceIncludeFormulaFields")
    def salesforce_include_formula_fields(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "salesforceIncludeFormulaFields"))

    @salesforce_include_formula_fields.setter
    def salesforce_include_formula_fields(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f8ebb784c683b044796608868e882b151112d1a39412cfff5fc75969dcfb654)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "salesforceIncludeFormulaFields", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scdType")
    def scd_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scdType"))

    @scd_type.setter
    def scd_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a1a54ae47ceeb0b1ef80717d4760a8ece661defe859be04403207a2cb814b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scdType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequenceBy")
    def sequence_by(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sequenceBy"))

    @sequence_by.setter
    def sequence_by(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d1f72f7cfaeb31938144ee39d748622a39acb6e8929b9e027d5cdcb304c009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequenceBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionTableConfiguration]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionTableConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionTableConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceaa0be954ba78f4a43b121644f22178ad0732c6fc98a893c77c64e0a951b674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cursor_columns": "cursorColumns",
        "deletion_condition": "deletionCondition",
        "hard_deletion_sync_min_interval_in_seconds": "hardDeletionSyncMinIntervalInSeconds",
    },
)
class PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig:
    def __init__(
        self,
        *,
        cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        deletion_condition: typing.Optional[builtins.str] = None,
        hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cursor_columns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.
        :param deletion_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.
        :param hard_deletion_sync_min_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__667591fa5f7ce9446962be5fc0664ba899a7c109078194d21892236b5780f510)
            check_type(argname="argument cursor_columns", value=cursor_columns, expected_type=type_hints["cursor_columns"])
            check_type(argname="argument deletion_condition", value=deletion_condition, expected_type=type_hints["deletion_condition"])
            check_type(argname="argument hard_deletion_sync_min_interval_in_seconds", value=hard_deletion_sync_min_interval_in_seconds, expected_type=type_hints["hard_deletion_sync_min_interval_in_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cursor_columns is not None:
            self._values["cursor_columns"] = cursor_columns
        if deletion_condition is not None:
            self._values["deletion_condition"] = deletion_condition
        if hard_deletion_sync_min_interval_in_seconds is not None:
            self._values["hard_deletion_sync_min_interval_in_seconds"] = hard_deletion_sync_min_interval_in_seconds

    @builtins.property
    def cursor_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cursor_columns Pipeline#cursor_columns}.'''
        result = self._values.get("cursor_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deletion_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#deletion_condition Pipeline#deletion_condition}.'''
        result = self._values.get("deletion_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hard_deletion_sync_min_interval_in_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#hard_deletion_sync_min_interval_in_seconds Pipeline#hard_deletion_sync_min_interval_in_seconds}.'''
        result = self._values.get("hard_deletion_sync_min_interval_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e403a9c507163806e65d55a2eb9774f928b42f267f07fd17f03b330cb6952dc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCursorColumns")
    def reset_cursor_columns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCursorColumns", []))

    @jsii.member(jsii_name="resetDeletionCondition")
    def reset_deletion_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionCondition", []))

    @jsii.member(jsii_name="resetHardDeletionSyncMinIntervalInSeconds")
    def reset_hard_deletion_sync_min_interval_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardDeletionSyncMinIntervalInSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="cursorColumnsInput")
    def cursor_columns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cursorColumnsInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionConditionInput")
    def deletion_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deletionConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSecondsInput")
    def hard_deletion_sync_min_interval_in_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardDeletionSyncMinIntervalInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="cursorColumns")
    def cursor_columns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cursorColumns"))

    @cursor_columns.setter
    def cursor_columns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a25817a7c165bd2363f4b3ec8a2ea765130dc0ff4c122edaaf98af778d4056a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cursorColumns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionCondition")
    def deletion_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletionCondition"))

    @deletion_condition.setter
    def deletion_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ad2195077e75f4098c5c6d9f8257b625f5c5b926d8d1c411440a567fe1024b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardDeletionSyncMinIntervalInSeconds")
    def hard_deletion_sync_min_interval_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardDeletionSyncMinIntervalInSeconds"))

    @hard_deletion_sync_min_interval_in_seconds.setter
    def hard_deletion_sync_min_interval_in_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f1e4e35d81147ec9abc08bd5939cfeccecc34dfd1d35d15342ea30fb958ee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardDeletionSyncMinIntervalInSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig]:
        return typing.cast(typing.Optional[PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4af82f34c4da66ee6358f538caa92262b0848b1e33857209f354a27c9e42bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLatestUpdates",
    jsii_struct_bases=[],
    name_mapping={
        "creation_time": "creationTime",
        "state": "state",
        "update_id": "updateId",
    },
)
class PipelineLatestUpdates:
    def __init__(
        self,
        *,
        creation_time: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        update_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param creation_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#creation_time Pipeline#creation_time}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#state Pipeline#state}.
        :param update_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#update_id Pipeline#update_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__895aae5df6cd73f482c61408bb3ca47b2bf12088f0accf06db90715bb3539c8a)
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument update_id", value=update_id, expected_type=type_hints["update_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if state is not None:
            self._values["state"] = state
        if update_id is not None:
            self._values["update_id"] = update_id

    @builtins.property
    def creation_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#creation_time Pipeline#creation_time}.'''
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#state Pipeline#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#update_id Pipeline#update_id}.'''
        result = self._values.get("update_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLatestUpdates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineLatestUpdatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLatestUpdatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a502ea6ca2085c438b87cd238aa8335953e4eb733b8819050db91b7d926d33cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PipelineLatestUpdatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57b810beaf2d9514b98e51d4fee615d4fa8c9df31a6211320ab384b3eb6eb941)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineLatestUpdatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc71ec804cd6102f1cd12fedf8dd3df5fe52265b9911acf0ee8f4c8b23a5e59)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b2f5172dfaf37353fc605f9f23bd9d80ba915a6d5c16b725c3c695c3c07edf1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc213ffcaaecd3e4d2b0d037f622466a6125feee82db09ff7193b2965a9f93ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLatestUpdates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLatestUpdates]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLatestUpdates]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dab1f6014a1e99b27a5f516ed45905943653cb0c47b8ec93a34130410fa34819)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineLatestUpdatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLatestUpdatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e925ea5ca6cfd9fbb5cd3f3d74e64dc1f9ad1df7bca25490fed9eec6b201409)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreationTime")
    def reset_creation_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationTime", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetUpdateId")
    def reset_update_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateId", []))

    @builtins.property
    @jsii.member(jsii_name="creationTimeInput")
    def creation_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="updateIdInput")
    def update_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @creation_time.setter
    def creation_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2365643e61047b21119ca58a72b91c7800089c583d7d7ce5f1e06a59043c979f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d199bc209c288b5c26926ce24c9fca9b55578a4fbefd9b54312e33b8954d7c03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updateId")
    def update_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateId"))

    @update_id.setter
    def update_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0639c76f02a7ac5ac6cb9d981bfe795dea55fe3c0a413a39cb421426221cadba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLatestUpdates]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLatestUpdates]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLatestUpdates]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71db015f94aaec17d87a59229595e4d8c87183f286fa4dd7c0aaef2845f9a685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibrary",
    jsii_struct_bases=[],
    name_mapping={
        "file": "file",
        "glob": "glob",
        "jar": "jar",
        "maven": "maven",
        "notebook": "notebook",
        "whl": "whl",
    },
)
class PipelineLibrary:
    def __init__(
        self,
        *,
        file: typing.Optional[typing.Union["PipelineLibraryFile", typing.Dict[builtins.str, typing.Any]]] = None,
        glob: typing.Optional[typing.Union["PipelineLibraryGlob", typing.Dict[builtins.str, typing.Any]]] = None,
        jar: typing.Optional[builtins.str] = None,
        maven: typing.Optional[typing.Union["PipelineLibraryMaven", typing.Dict[builtins.str, typing.Any]]] = None,
        notebook: typing.Optional[typing.Union["PipelineLibraryNotebook", typing.Dict[builtins.str, typing.Any]]] = None,
        whl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#file Pipeline#file}
        :param glob: glob block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#glob Pipeline#glob}
        :param jar: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#jar Pipeline#jar}.
        :param maven: maven block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#maven Pipeline#maven}
        :param notebook: notebook block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#notebook Pipeline#notebook}
        :param whl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#whl Pipeline#whl}.
        '''
        if isinstance(file, dict):
            file = PipelineLibraryFile(**file)
        if isinstance(glob, dict):
            glob = PipelineLibraryGlob(**glob)
        if isinstance(maven, dict):
            maven = PipelineLibraryMaven(**maven)
        if isinstance(notebook, dict):
            notebook = PipelineLibraryNotebook(**notebook)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1560db388e699f602e6ac52c25d07e99ae4739291fccfdd3ef0f687168e8ba0e)
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument glob", value=glob, expected_type=type_hints["glob"])
            check_type(argname="argument jar", value=jar, expected_type=type_hints["jar"])
            check_type(argname="argument maven", value=maven, expected_type=type_hints["maven"])
            check_type(argname="argument notebook", value=notebook, expected_type=type_hints["notebook"])
            check_type(argname="argument whl", value=whl, expected_type=type_hints["whl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file is not None:
            self._values["file"] = file
        if glob is not None:
            self._values["glob"] = glob
        if jar is not None:
            self._values["jar"] = jar
        if maven is not None:
            self._values["maven"] = maven
        if notebook is not None:
            self._values["notebook"] = notebook
        if whl is not None:
            self._values["whl"] = whl

    @builtins.property
    def file(self) -> typing.Optional["PipelineLibraryFile"]:
        '''file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#file Pipeline#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional["PipelineLibraryFile"], result)

    @builtins.property
    def glob(self) -> typing.Optional["PipelineLibraryGlob"]:
        '''glob block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#glob Pipeline#glob}
        '''
        result = self._values.get("glob")
        return typing.cast(typing.Optional["PipelineLibraryGlob"], result)

    @builtins.property
    def jar(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#jar Pipeline#jar}.'''
        result = self._values.get("jar")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven(self) -> typing.Optional["PipelineLibraryMaven"]:
        '''maven block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#maven Pipeline#maven}
        '''
        result = self._values.get("maven")
        return typing.cast(typing.Optional["PipelineLibraryMaven"], result)

    @builtins.property
    def notebook(self) -> typing.Optional["PipelineLibraryNotebook"]:
        '''notebook block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#notebook Pipeline#notebook}
        '''
        result = self._values.get("notebook")
        return typing.cast(typing.Optional["PipelineLibraryNotebook"], result)

    @builtins.property
    def whl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#whl Pipeline#whl}.'''
        result = self._values.get("whl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLibrary(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryFile",
    jsii_struct_bases=[],
    name_mapping={"path": "path"},
)
class PipelineLibraryFile:
    def __init__(self, *, path: builtins.str) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__192b1582e89a77558f7d2a75c84672b81c976174fc27c8e72ef11a9eb19e340b)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLibraryFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineLibraryFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bf2ec7f1ace1c0d2ec678e0e65e01cab49bd5975158d18d0bf9b4ec34037109)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40672a15b893cc08dc69580e935a86c0104348b94492b8638d3a2a65f656b803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineLibraryFile]:
        return typing.cast(typing.Optional[PipelineLibraryFile], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineLibraryFile]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0fdb0532d4df5702ddcab16ef42facf114a6452ccbf62d805c661515cbea490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryGlob",
    jsii_struct_bases=[],
    name_mapping={"include": "include"},
)
class PipelineLibraryGlob:
    def __init__(self, *, include: builtins.str) -> None:
        '''
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fadec0c6764a42b3d1e76418517426982ccaa020cdbf48a9dd760fa15eb6edf)
            check_type(argname="argument include", value=include, expected_type=type_hints["include"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "include": include,
        }

    @builtins.property
    def include(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.'''
        result = self._values.get("include")
        assert result is not None, "Required property 'include' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLibraryGlob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineLibraryGlobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryGlobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdccffd865df5823621a5b99f1ce81860d6cf509d4dc3dedce20668908d720e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="includeInput")
    def include_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includeInput"))

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "include"))

    @include.setter
    def include(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3ef50f795b455e937c2e5ebbea0713410574ce5f003eae1ac1de2fa8b3606fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineLibraryGlob]:
        return typing.cast(typing.Optional[PipelineLibraryGlob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineLibraryGlob]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842e1a3bea8fbc34c854bb8f3b066e3bd78902179a4b422b751712b189d48216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineLibraryList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2a34acb76d8cd2be5799f8197c24a91a9c058cf0892e0c1b95624ebd82ea827)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PipelineLibraryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8fae7c549a6fe248c9ea15add8d076fa7d0ab5da97065b2eb32978e5da17135)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineLibraryOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88ef3f0dae6ba61576eb56c990d211faeff9c36d337f212c3a2978e674cb2e54)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c02cfb6a77773185cc2b602c7d4ce629a92a23d34578db120afec6e87eec4e44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b81557bf514c98f27c1b18f480bd80030803111d0839da4da3ea0df6e719412e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLibrary]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLibrary]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLibrary]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__941b428873e6206e24d64787e0d7fa0e7270b773f845a0d4257899f99088afb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryMaven",
    jsii_struct_bases=[],
    name_mapping={
        "coordinates": "coordinates",
        "exclusions": "exclusions",
        "repo": "repo",
    },
)
class PipelineLibraryMaven:
    def __init__(
        self,
        *,
        coordinates: builtins.str,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param coordinates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#coordinates Pipeline#coordinates}.
        :param exclusions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclusions Pipeline#exclusions}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#repo Pipeline#repo}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9762510eb02d8bbbd37281914c774f22bfee1e1ed949ea55fff9b25c52f854e)
            check_type(argname="argument coordinates", value=coordinates, expected_type=type_hints["coordinates"])
            check_type(argname="argument exclusions", value=exclusions, expected_type=type_hints["exclusions"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "coordinates": coordinates,
        }
        if exclusions is not None:
            self._values["exclusions"] = exclusions
        if repo is not None:
            self._values["repo"] = repo

    @builtins.property
    def coordinates(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#coordinates Pipeline#coordinates}.'''
        result = self._values.get("coordinates")
        assert result is not None, "Required property 'coordinates' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclusions Pipeline#exclusions}.'''
        result = self._values.get("exclusions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repo(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#repo Pipeline#repo}.'''
        result = self._values.get("repo")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLibraryMaven(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineLibraryMavenOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryMavenOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39bba964e08c67dc8a4f2ec6d7d2fcbe1f65158087cdf4c528ef2efd1d2cb0ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExclusions")
    def reset_exclusions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExclusions", []))

    @jsii.member(jsii_name="resetRepo")
    def reset_repo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepo", []))

    @builtins.property
    @jsii.member(jsii_name="coordinatesInput")
    def coordinates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coordinatesInput"))

    @builtins.property
    @jsii.member(jsii_name="exclusionsInput")
    def exclusions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclusionsInput"))

    @builtins.property
    @jsii.member(jsii_name="repoInput")
    def repo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoInput"))

    @builtins.property
    @jsii.member(jsii_name="coordinates")
    def coordinates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coordinates"))

    @coordinates.setter
    def coordinates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1402f8c23a02f838e6aeb7a940d807ccd0df50604e2741cf15196de2428ff377)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coordinates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclusions"))

    @exclusions.setter
    def exclusions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0207077b5abe91b53c1a981032064b7b4d91f084db71e9bc6da546e896c32cc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclusions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repo")
    def repo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repo"))

    @repo.setter
    def repo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f3146760112fefb2bd67fcfa97a81ecf9a00613ce6a2ee488d5b951c17f8be0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineLibraryMaven]:
        return typing.cast(typing.Optional[PipelineLibraryMaven], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineLibraryMaven]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8511b3696b259df3391b274a544f46e94af97b8b8e09fd3d7dd1a79db7f8f82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryNotebook",
    jsii_struct_bases=[],
    name_mapping={"path": "path"},
)
class PipelineLibraryNotebook:
    def __init__(self, *, path: builtins.str) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc8590d33fb32f1842216fa9e717031b1dc856c5fa176183fff2199431d6a380)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineLibraryNotebook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineLibraryNotebookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryNotebookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bd01d3abdeef70a00f986c4df9c71bb53ac71bed2f6d99bdcfd737708d2cd83)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a24326d322804cb172a6c36232fc5a8c14d356d7aa70ed84c1638fe51befac8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineLibraryNotebook]:
        return typing.cast(typing.Optional[PipelineLibraryNotebook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineLibraryNotebook]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817625d545c00883dba62ebec6721f41c983682d781d9a73349430f24f35434e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineLibraryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineLibraryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47584481f20b041090a41d476358cfb193b50b8ed354784137955510a7635938)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFile")
    def put_file(self, *, path: builtins.str) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.
        '''
        value = PipelineLibraryFile(path=path)

        return typing.cast(None, jsii.invoke(self, "putFile", [value]))

    @jsii.member(jsii_name="putGlob")
    def put_glob(self, *, include: builtins.str) -> None:
        '''
        :param include: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#include Pipeline#include}.
        '''
        value = PipelineLibraryGlob(include=include)

        return typing.cast(None, jsii.invoke(self, "putGlob", [value]))

    @jsii.member(jsii_name="putMaven")
    def put_maven(
        self,
        *,
        coordinates: builtins.str,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        repo: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param coordinates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#coordinates Pipeline#coordinates}.
        :param exclusions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#exclusions Pipeline#exclusions}.
        :param repo: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#repo Pipeline#repo}.
        '''
        value = PipelineLibraryMaven(
            coordinates=coordinates, exclusions=exclusions, repo=repo
        )

        return typing.cast(None, jsii.invoke(self, "putMaven", [value]))

    @jsii.member(jsii_name="putNotebook")
    def put_notebook(self, *, path: builtins.str) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#path Pipeline#path}.
        '''
        value = PipelineLibraryNotebook(path=path)

        return typing.cast(None, jsii.invoke(self, "putNotebook", [value]))

    @jsii.member(jsii_name="resetFile")
    def reset_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFile", []))

    @jsii.member(jsii_name="resetGlob")
    def reset_glob(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlob", []))

    @jsii.member(jsii_name="resetJar")
    def reset_jar(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJar", []))

    @jsii.member(jsii_name="resetMaven")
    def reset_maven(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaven", []))

    @jsii.member(jsii_name="resetNotebook")
    def reset_notebook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotebook", []))

    @jsii.member(jsii_name="resetWhl")
    def reset_whl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhl", []))

    @builtins.property
    @jsii.member(jsii_name="file")
    def file(self) -> PipelineLibraryFileOutputReference:
        return typing.cast(PipelineLibraryFileOutputReference, jsii.get(self, "file"))

    @builtins.property
    @jsii.member(jsii_name="glob")
    def glob(self) -> PipelineLibraryGlobOutputReference:
        return typing.cast(PipelineLibraryGlobOutputReference, jsii.get(self, "glob"))

    @builtins.property
    @jsii.member(jsii_name="maven")
    def maven(self) -> PipelineLibraryMavenOutputReference:
        return typing.cast(PipelineLibraryMavenOutputReference, jsii.get(self, "maven"))

    @builtins.property
    @jsii.member(jsii_name="notebook")
    def notebook(self) -> PipelineLibraryNotebookOutputReference:
        return typing.cast(PipelineLibraryNotebookOutputReference, jsii.get(self, "notebook"))

    @builtins.property
    @jsii.member(jsii_name="fileInput")
    def file_input(self) -> typing.Optional[PipelineLibraryFile]:
        return typing.cast(typing.Optional[PipelineLibraryFile], jsii.get(self, "fileInput"))

    @builtins.property
    @jsii.member(jsii_name="globInput")
    def glob_input(self) -> typing.Optional[PipelineLibraryGlob]:
        return typing.cast(typing.Optional[PipelineLibraryGlob], jsii.get(self, "globInput"))

    @builtins.property
    @jsii.member(jsii_name="jarInput")
    def jar_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jarInput"))

    @builtins.property
    @jsii.member(jsii_name="mavenInput")
    def maven_input(self) -> typing.Optional[PipelineLibraryMaven]:
        return typing.cast(typing.Optional[PipelineLibraryMaven], jsii.get(self, "mavenInput"))

    @builtins.property
    @jsii.member(jsii_name="notebookInput")
    def notebook_input(self) -> typing.Optional[PipelineLibraryNotebook]:
        return typing.cast(typing.Optional[PipelineLibraryNotebook], jsii.get(self, "notebookInput"))

    @builtins.property
    @jsii.member(jsii_name="whlInput")
    def whl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "whlInput"))

    @builtins.property
    @jsii.member(jsii_name="jar")
    def jar(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jar"))

    @jar.setter
    def jar(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a45e844c8624b48e6b9e2a60ee9a158a18e404859e4c00ba84f3a9af395c79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jar", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whl")
    def whl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "whl"))

    @whl.setter
    def whl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5ff5ad10a76fd765c1b4ab99c5fa0fb489a1501d5f98a8c69323110f970831b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLibrary]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLibrary]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLibrary]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f0f1330ccdcf68d22a72400fa4519013bc5e812b68193fc914bd4dd07ec9666)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineNotification",
    jsii_struct_bases=[],
    name_mapping={"alerts": "alerts", "email_recipients": "emailRecipients"},
)
class PipelineNotification:
    def __init__(
        self,
        *,
        alerts: typing.Optional[typing.Sequence[builtins.str]] = None,
        email_recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param alerts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#alerts Pipeline#alerts}.
        :param email_recipients: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#email_recipients Pipeline#email_recipients}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b8e401d03bcfbc10097c2395af05aff23ca1cdc689241b820c76ab6b8761602)
            check_type(argname="argument alerts", value=alerts, expected_type=type_hints["alerts"])
            check_type(argname="argument email_recipients", value=email_recipients, expected_type=type_hints["email_recipients"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alerts is not None:
            self._values["alerts"] = alerts
        if email_recipients is not None:
            self._values["email_recipients"] = email_recipients

    @builtins.property
    def alerts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#alerts Pipeline#alerts}.'''
        result = self._values.get("alerts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def email_recipients(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#email_recipients Pipeline#email_recipients}.'''
        result = self._values.get("email_recipients")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineNotificationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineNotificationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6aca95e7ece8bb109cea2c71e613419108b1ca2886cc42d59674f1f36bc21b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PipelineNotificationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a66e961227762c7b182c9167aa04f72f9bd31331e0546df3097c01a6a9e1a1d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PipelineNotificationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8231cd11af95102a530318792ce0d1f23673fe1b9f2c164179a6a7b213f0d414)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b85bacc1230974e08767a382bfae3194c400bdba21bbcdfcc7961c2c9e18fbb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea7d09f0bf3cf787a07796959ed668f6733c8814a8d24b420f9a0c74824dcd65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineNotification]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineNotification]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineNotification]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af3a27adbe8aabb5143af173954cd2b3ef3b906a41312c354837028a5734b82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineNotificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineNotificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61ad8747597828880f5cc8bc2efb25caa1ad683dc883428c18e99c410d461235)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAlerts")
    def reset_alerts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlerts", []))

    @jsii.member(jsii_name="resetEmailRecipients")
    def reset_email_recipients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailRecipients", []))

    @builtins.property
    @jsii.member(jsii_name="alertsInput")
    def alerts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "alertsInput"))

    @builtins.property
    @jsii.member(jsii_name="emailRecipientsInput")
    def email_recipients_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "emailRecipientsInput"))

    @builtins.property
    @jsii.member(jsii_name="alerts")
    def alerts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "alerts"))

    @alerts.setter
    def alerts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9054580b8a926c4b33655825efa87cdc724a30db1aeff0f21bc77a07cd3fc07a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alerts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailRecipients")
    def email_recipients(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "emailRecipients"))

    @email_recipients.setter
    def email_recipients(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__645b1e294b1de53b2f2eed598bd13922919608f76b48c84659597180c183c479)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailRecipients", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineNotification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineNotification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86723a1b41e3e00a1f3746f7e6f6c1aa26853ff57701cd2b6c95dc6f94412ffc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineRestartWindow",
    jsii_struct_bases=[],
    name_mapping={
        "start_hour": "startHour",
        "days_of_week": "daysOfWeek",
        "time_zone_id": "timeZoneId",
    },
)
class PipelineRestartWindow:
    def __init__(
        self,
        *,
        start_hour: jsii.Number,
        days_of_week: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param start_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#start_hour Pipeline#start_hour}.
        :param days_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#days_of_week Pipeline#days_of_week}.
        :param time_zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#time_zone_id Pipeline#time_zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eae16d3e94207d57131a361eaafa4b5539358d6ebdccb5b5775f832fc7302002)
            check_type(argname="argument start_hour", value=start_hour, expected_type=type_hints["start_hour"])
            check_type(argname="argument days_of_week", value=days_of_week, expected_type=type_hints["days_of_week"])
            check_type(argname="argument time_zone_id", value=time_zone_id, expected_type=type_hints["time_zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "start_hour": start_hour,
        }
        if days_of_week is not None:
            self._values["days_of_week"] = days_of_week
        if time_zone_id is not None:
            self._values["time_zone_id"] = time_zone_id

    @builtins.property
    def start_hour(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#start_hour Pipeline#start_hour}.'''
        result = self._values.get("start_hour")
        assert result is not None, "Required property 'start_hour' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def days_of_week(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#days_of_week Pipeline#days_of_week}.'''
        result = self._values.get("days_of_week")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def time_zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#time_zone_id Pipeline#time_zone_id}.'''
        result = self._values.get("time_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineRestartWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineRestartWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineRestartWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ef5c574f99738eadffd2c5203b5d7859d0f204f7e32b352c7382dd621b2d2eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDaysOfWeek")
    def reset_days_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDaysOfWeek", []))

    @jsii.member(jsii_name="resetTimeZoneId")
    def reset_time_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="daysOfWeekInput")
    def days_of_week_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "daysOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="startHourInput")
    def start_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startHourInput"))

    @builtins.property
    @jsii.member(jsii_name="timeZoneIdInput")
    def time_zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeZoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="daysOfWeek")
    def days_of_week(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "daysOfWeek"))

    @days_of_week.setter
    def days_of_week(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcf8c184f5d530129f94ae7967e01c8ee91a7bd908b86127412063c5c4e10dd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "daysOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startHour")
    def start_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startHour"))

    @start_hour.setter
    def start_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__586b6d27815c47c1150a06655ee5ec4413fe12ad40838b07be3bea518548f65f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZoneId")
    def time_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZoneId"))

    @time_zone_id.setter
    def time_zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d09bdda7e7d76f8c0c0023b5169a821dbe5ebc56a9bb80b96b3959ace55e7011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineRestartWindow]:
        return typing.cast(typing.Optional[PipelineRestartWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineRestartWindow]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551120e83a958de2a491b35a302fc87b3381660f18f95dee28eebf552610cec2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineRunAs",
    jsii_struct_bases=[],
    name_mapping={
        "service_principal_name": "servicePrincipalName",
        "user_name": "userName",
    },
)
class PipelineRunAs:
    def __init__(
        self,
        *,
        service_principal_name: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_principal_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#service_principal_name Pipeline#service_principal_name}.
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#user_name Pipeline#user_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b452b7e6bebe803bd3cca3b0b5e5278db4085c60b5dd7c4d4976f8ec60eaf5)
            check_type(argname="argument service_principal_name", value=service_principal_name, expected_type=type_hints["service_principal_name"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if service_principal_name is not None:
            self._values["service_principal_name"] = service_principal_name
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def service_principal_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#service_principal_name Pipeline#service_principal_name}.'''
        result = self._values.get("service_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#user_name Pipeline#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineRunAs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineRunAsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineRunAsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2643619a09f82661aec1e1c79e6b2b2a836bc7d22161ea98677a37a4aa7dd084)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetServicePrincipalName")
    def reset_service_principal_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServicePrincipalName", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalNameInput")
    def service_principal_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servicePrincipalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalName")
    def service_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalName"))

    @service_principal_name.setter
    def service_principal_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211304b79a4dffa799194b0cdf28972bb202e147bb69975b3e022a3f3969b2f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c45bb5273aabad412146b5f151305fffd91cd37fdf0579eabe1687a52982919d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineRunAs]:
        return typing.cast(typing.Optional[PipelineRunAs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineRunAs]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faa15c557c4b44abe8e1d01176999f496294b405ce8d6aa0eccf65984eebdc8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTimeouts",
    jsii_struct_bases=[],
    name_mapping={"default": "default"},
)
class PipelineTimeouts:
    def __init__(self, *, default: typing.Optional[builtins.str] = None) -> None:
        '''
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#default Pipeline#default}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d29c3e7df634a524db84f9a53d81f360f05c83c2ec781945dacda30bf99870f)
            check_type(argname="argument default", value=default, expected_type=type_hints["default"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if default is not None:
            self._values["default"] = default

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#default Pipeline#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e6138e05ec93a75d7b4f682852e48e678e156b29ba62c26e91be52b6fe2832e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDefault")
    def reset_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefault", []))

    @builtins.property
    @jsii.member(jsii_name="defaultInput")
    def default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultInput"))

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce2a0e7ccdfefb3633410370e0db3ad2b806ea247f04f6840b571828b8ec66b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9233c8fdd8e60986f1c4a536efc1c3d0ba0a28cf879ddc46c63c06f833ef0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTrigger",
    jsii_struct_bases=[],
    name_mapping={"cron": "cron", "manual": "manual"},
)
class PipelineTrigger:
    def __init__(
        self,
        *,
        cron: typing.Optional[typing.Union["PipelineTriggerCron", typing.Dict[builtins.str, typing.Any]]] = None,
        manual: typing.Optional[typing.Union["PipelineTriggerManual", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cron: cron block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cron Pipeline#cron}
        :param manual: manual block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#manual Pipeline#manual}
        '''
        if isinstance(cron, dict):
            cron = PipelineTriggerCron(**cron)
        if isinstance(manual, dict):
            manual = PipelineTriggerManual(**manual)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__271e32d0c972c04975b2ee92c62afec49ec6ac91cb5cecf8f44bd1cd83c9e62a)
            check_type(argname="argument cron", value=cron, expected_type=type_hints["cron"])
            check_type(argname="argument manual", value=manual, expected_type=type_hints["manual"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cron is not None:
            self._values["cron"] = cron
        if manual is not None:
            self._values["manual"] = manual

    @builtins.property
    def cron(self) -> typing.Optional["PipelineTriggerCron"]:
        '''cron block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#cron Pipeline#cron}
        '''
        result = self._values.get("cron")
        return typing.cast(typing.Optional["PipelineTriggerCron"], result)

    @builtins.property
    def manual(self) -> typing.Optional["PipelineTriggerManual"]:
        '''manual block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#manual Pipeline#manual}
        '''
        result = self._values.get("manual")
        return typing.cast(typing.Optional["PipelineTriggerManual"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineTrigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTriggerCron",
    jsii_struct_bases=[],
    name_mapping={
        "quartz_cron_schedule": "quartzCronSchedule",
        "timezone_id": "timezoneId",
    },
)
class PipelineTriggerCron:
    def __init__(
        self,
        *,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#quartz_cron_schedule Pipeline#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timezone_id Pipeline#timezone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3966946f020634493f35aa45fddfca6075af2b0675820ffa1a9aa1ea1891ea)
            check_type(argname="argument quartz_cron_schedule", value=quartz_cron_schedule, expected_type=type_hints["quartz_cron_schedule"])
            check_type(argname="argument timezone_id", value=timezone_id, expected_type=type_hints["timezone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if quartz_cron_schedule is not None:
            self._values["quartz_cron_schedule"] = quartz_cron_schedule
        if timezone_id is not None:
            self._values["timezone_id"] = timezone_id

    @builtins.property
    def quartz_cron_schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#quartz_cron_schedule Pipeline#quartz_cron_schedule}.'''
        result = self._values.get("quartz_cron_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timezone_id Pipeline#timezone_id}.'''
        result = self._values.get("timezone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineTriggerCron(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineTriggerCronOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTriggerCronOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8af87d2810d9ea58541714cd57e338795e8a5b5fa241df8c40caab0eddd1e4eb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetQuartzCronSchedule")
    def reset_quartz_cron_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuartzCronSchedule", []))

    @jsii.member(jsii_name="resetTimezoneId")
    def reset_timezone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezoneId", []))

    @builtins.property
    @jsii.member(jsii_name="quartzCronScheduleInput")
    def quartz_cron_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "quartzCronScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="timezoneIdInput")
    def timezone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="quartzCronSchedule")
    def quartz_cron_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "quartzCronSchedule"))

    @quartz_cron_schedule.setter
    def quartz_cron_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b394f184f8ba5b9108ac5b1afb8247ac895577be21eec0aae58b751ba9b6059)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "quartzCronSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezoneId")
    def timezone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezoneId"))

    @timezone_id.setter
    def timezone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bd8f92aeaca56a9ff9cfc34a6ce67987709178d7e3cbb931a6fd9d27f1babc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineTriggerCron]:
        return typing.cast(typing.Optional[PipelineTriggerCron], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineTriggerCron]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5006399dcc1282a9dcdd9a4b62baec6f88ecd8c73f44ecacd0675bd5a8d61dc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTriggerManual",
    jsii_struct_bases=[],
    name_mapping={},
)
class PipelineTriggerManual:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineTriggerManual(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineTriggerManualOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTriggerManualOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__524b872e03f68f6b8673f42f832d502e945ad7b4c184de23231d283bff82751c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineTriggerManual]:
        return typing.cast(typing.Optional[PipelineTriggerManual], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineTriggerManual]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33579b5f50a2aaff25d0a8a57cb1f682ec606552ab4df6758356070eb81c17da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PipelineTriggerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.pipeline.PipelineTriggerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d6644db1b269cf8893b6b595908b497243aead9d5b10332353d990fdb58ac2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCron")
    def put_cron(
        self,
        *,
        quartz_cron_schedule: typing.Optional[builtins.str] = None,
        timezone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param quartz_cron_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#quartz_cron_schedule Pipeline#quartz_cron_schedule}.
        :param timezone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.88.0/docs/resources/pipeline#timezone_id Pipeline#timezone_id}.
        '''
        value = PipelineTriggerCron(
            quartz_cron_schedule=quartz_cron_schedule, timezone_id=timezone_id
        )

        return typing.cast(None, jsii.invoke(self, "putCron", [value]))

    @jsii.member(jsii_name="putManual")
    def put_manual(self) -> None:
        value = PipelineTriggerManual()

        return typing.cast(None, jsii.invoke(self, "putManual", [value]))

    @jsii.member(jsii_name="resetCron")
    def reset_cron(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCron", []))

    @jsii.member(jsii_name="resetManual")
    def reset_manual(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManual", []))

    @builtins.property
    @jsii.member(jsii_name="cron")
    def cron(self) -> PipelineTriggerCronOutputReference:
        return typing.cast(PipelineTriggerCronOutputReference, jsii.get(self, "cron"))

    @builtins.property
    @jsii.member(jsii_name="manual")
    def manual(self) -> PipelineTriggerManualOutputReference:
        return typing.cast(PipelineTriggerManualOutputReference, jsii.get(self, "manual"))

    @builtins.property
    @jsii.member(jsii_name="cronInput")
    def cron_input(self) -> typing.Optional[PipelineTriggerCron]:
        return typing.cast(typing.Optional[PipelineTriggerCron], jsii.get(self, "cronInput"))

    @builtins.property
    @jsii.member(jsii_name="manualInput")
    def manual_input(self) -> typing.Optional[PipelineTriggerManual]:
        return typing.cast(typing.Optional[PipelineTriggerManual], jsii.get(self, "manualInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PipelineTrigger]:
        return typing.cast(typing.Optional[PipelineTrigger], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PipelineTrigger]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24eba4b5fda8deeac8ce0db24da149fa91faf3b1933039eae9e4f78fcdfd5b87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Pipeline",
    "PipelineCluster",
    "PipelineClusterAutoscale",
    "PipelineClusterAutoscaleOutputReference",
    "PipelineClusterAwsAttributes",
    "PipelineClusterAwsAttributesOutputReference",
    "PipelineClusterAzureAttributes",
    "PipelineClusterAzureAttributesLogAnalyticsInfo",
    "PipelineClusterAzureAttributesLogAnalyticsInfoOutputReference",
    "PipelineClusterAzureAttributesOutputReference",
    "PipelineClusterClusterLogConf",
    "PipelineClusterClusterLogConfDbfs",
    "PipelineClusterClusterLogConfDbfsOutputReference",
    "PipelineClusterClusterLogConfOutputReference",
    "PipelineClusterClusterLogConfS3",
    "PipelineClusterClusterLogConfS3OutputReference",
    "PipelineClusterClusterLogConfVolumes",
    "PipelineClusterClusterLogConfVolumesOutputReference",
    "PipelineClusterGcpAttributes",
    "PipelineClusterGcpAttributesOutputReference",
    "PipelineClusterInitScripts",
    "PipelineClusterInitScriptsAbfss",
    "PipelineClusterInitScriptsAbfssOutputReference",
    "PipelineClusterInitScriptsDbfs",
    "PipelineClusterInitScriptsDbfsOutputReference",
    "PipelineClusterInitScriptsFile",
    "PipelineClusterInitScriptsFileOutputReference",
    "PipelineClusterInitScriptsGcs",
    "PipelineClusterInitScriptsGcsOutputReference",
    "PipelineClusterInitScriptsList",
    "PipelineClusterInitScriptsOutputReference",
    "PipelineClusterInitScriptsS3",
    "PipelineClusterInitScriptsS3OutputReference",
    "PipelineClusterInitScriptsVolumes",
    "PipelineClusterInitScriptsVolumesOutputReference",
    "PipelineClusterInitScriptsWorkspace",
    "PipelineClusterInitScriptsWorkspaceOutputReference",
    "PipelineClusterList",
    "PipelineClusterOutputReference",
    "PipelineConfig",
    "PipelineDeployment",
    "PipelineDeploymentOutputReference",
    "PipelineEnvironment",
    "PipelineEnvironmentOutputReference",
    "PipelineEventLog",
    "PipelineEventLogOutputReference",
    "PipelineFilters",
    "PipelineFiltersOutputReference",
    "PipelineGatewayDefinition",
    "PipelineGatewayDefinitionOutputReference",
    "PipelineIngestionDefinition",
    "PipelineIngestionDefinitionObjects",
    "PipelineIngestionDefinitionObjectsList",
    "PipelineIngestionDefinitionObjectsOutputReference",
    "PipelineIngestionDefinitionObjectsReport",
    "PipelineIngestionDefinitionObjectsReportOutputReference",
    "PipelineIngestionDefinitionObjectsReportTableConfiguration",
    "PipelineIngestionDefinitionObjectsReportTableConfigurationOutputReference",
    "PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig",
    "PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfigOutputReference",
    "PipelineIngestionDefinitionObjectsSchema",
    "PipelineIngestionDefinitionObjectsSchemaOutputReference",
    "PipelineIngestionDefinitionObjectsSchemaTableConfiguration",
    "PipelineIngestionDefinitionObjectsSchemaTableConfigurationOutputReference",
    "PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig",
    "PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfigOutputReference",
    "PipelineIngestionDefinitionObjectsTable",
    "PipelineIngestionDefinitionObjectsTableOutputReference",
    "PipelineIngestionDefinitionObjectsTableTableConfiguration",
    "PipelineIngestionDefinitionObjectsTableTableConfigurationOutputReference",
    "PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig",
    "PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfigOutputReference",
    "PipelineIngestionDefinitionOutputReference",
    "PipelineIngestionDefinitionSourceConfigurations",
    "PipelineIngestionDefinitionSourceConfigurationsCatalog",
    "PipelineIngestionDefinitionSourceConfigurationsCatalogOutputReference",
    "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres",
    "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresOutputReference",
    "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig",
    "PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfigOutputReference",
    "PipelineIngestionDefinitionSourceConfigurationsList",
    "PipelineIngestionDefinitionSourceConfigurationsOutputReference",
    "PipelineIngestionDefinitionTableConfiguration",
    "PipelineIngestionDefinitionTableConfigurationOutputReference",
    "PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig",
    "PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfigOutputReference",
    "PipelineLatestUpdates",
    "PipelineLatestUpdatesList",
    "PipelineLatestUpdatesOutputReference",
    "PipelineLibrary",
    "PipelineLibraryFile",
    "PipelineLibraryFileOutputReference",
    "PipelineLibraryGlob",
    "PipelineLibraryGlobOutputReference",
    "PipelineLibraryList",
    "PipelineLibraryMaven",
    "PipelineLibraryMavenOutputReference",
    "PipelineLibraryNotebook",
    "PipelineLibraryNotebookOutputReference",
    "PipelineLibraryOutputReference",
    "PipelineNotification",
    "PipelineNotificationList",
    "PipelineNotificationOutputReference",
    "PipelineRestartWindow",
    "PipelineRestartWindowOutputReference",
    "PipelineRunAs",
    "PipelineRunAsOutputReference",
    "PipelineTimeouts",
    "PipelineTimeoutsOutputReference",
    "PipelineTrigger",
    "PipelineTriggerCron",
    "PipelineTriggerCronOutputReference",
    "PipelineTriggerManual",
    "PipelineTriggerManualOutputReference",
    "PipelineTriggerOutputReference",
]

publication.publish()

def _typecheckingstub__d0bf98735978227a74d3563ac743f858b0ee60db9c653153e602bcf484da355f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    allow_duplicate_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    catalog: typing.Optional[builtins.str] = None,
    cause: typing.Optional[builtins.str] = None,
    channel: typing.Optional[builtins.str] = None,
    cluster: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineCluster, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    configuration: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    continuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    creator_user_name: typing.Optional[builtins.str] = None,
    deployment: typing.Optional[typing.Union[PipelineDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    development: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    edition: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Union[PipelineEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    event_log: typing.Optional[typing.Union[PipelineEventLog, typing.Dict[builtins.str, typing.Any]]] = None,
    expected_last_modified: typing.Optional[jsii.Number] = None,
    filters: typing.Optional[typing.Union[PipelineFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    gateway_definition: typing.Optional[typing.Union[PipelineGatewayDefinition, typing.Dict[builtins.str, typing.Any]]] = None,
    health: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ingestion_definition: typing.Optional[typing.Union[PipelineIngestionDefinition, typing.Dict[builtins.str, typing.Any]]] = None,
    last_modified: typing.Optional[jsii.Number] = None,
    latest_updates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLatestUpdates, typing.Dict[builtins.str, typing.Any]]]]] = None,
    library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLibrary, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineNotification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    restart_window: typing.Optional[typing.Union[PipelineRestartWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    root_path: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[PipelineRunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
    serverless: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    state: typing.Optional[builtins.str] = None,
    storage: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    target: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[PipelineTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    trigger: typing.Optional[typing.Union[PipelineTrigger, typing.Dict[builtins.str, typing.Any]]] = None,
    url: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e79f98be421668ee66ea6484d27e20efb71e6167145f9f4f52521307895c1e9c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__686f058a1524241956419cb676489836151d4f1cbc411aafe6df3f21e8cb497f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineCluster, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca318dc3a600244706ba5c10ccd71acb4a5c04fe891e17bd4373a1ea359c591(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLatestUpdates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__718051e6297cf70b4433c1dc18d1514e18bda33aa43b59951fed173deee71445(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLibrary, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae2ffd87d23f97fff4978ba983ffa8f06b698de24c0d629ea578a2e012f2840(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineNotification, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc9504f8da036eea33cd9d2fa16e93a946738866c0f20f792eafc46b930f7623(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8801f174a1eebadd84afd14e643f8df847264825ce3d10d2d51ed9909012fa2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62ac2805211275e46dbbeeb48262da2e18af8958f90c77a563416d57d2f8e66f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf06f6c0c601c3f3f742350445815f36b0c9a79c21e234dd977622ddfdb781f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38565a30cf245e322d591c06e2a2e27b56dcfea061aa3d6a31ad44f119e2831a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__569c5ec975959b273e537c17b09d80f01e4d3677263ae67fa8917ac2cb6e3fc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82d6f9c5b4a4b60e61b94a5b9fdcb486145d545ddd39214f47c588d695cf51a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d776bac6cd09f0f317f6e9fe6d7e371df1bcc9ce780b60302c97da1ba9723258(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45ab4cf5ff8025960a032974b2c993b8e6f74bac4f3eb71f45cdfc366dee9ed0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b7bbbf776ad3ddaf8df1fd8e0bbd5a572dd86c328ee3fd5414edded35871869(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfecfa3fab80f92ee4b1e05c2036a993352ee072593957b5c091181dde1d0843(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__936c9b1e76ec4feab4ecc032ea16c5064c047f5123fded545325b8b96917ab56(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f939a28797f941dac3959266dd9919dd59a4855198790407bfa2aace70b5f53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340a3daffd53a98b8ac2eb1e1814feb8b0cd9b3e219801ebf86069ded5dd83ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afc2fb866b548a23aff8122b2c51572f919a5dffec5080ba8ffcdaf0e3abe9f8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52914df0ba6a3df04d8e2e4a9793eae1dd3bfe17fdef6941e43dd82cb7dd0e66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54ce1e56fa768f54ef0ef4788516029aac7b814c759a8167e2e06168aff726e8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f365a53a7af7f1dcf74aaf41eddcbf1d5b1c9166fa9a5f8f8213628f1f76d41f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66f635c1e46ba212487df93c5bec58a6787a1d1cc7066575713957d030c00c1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__876b9a513ec60441a6a2ed714abb4476a65d8000266eb6d76e64f985ccb62526(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a2d03895dcb1012266dc2e6639332747dd69239a74e4ca375f5923e9212e2f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef46bfbec16dfa39a424e12b1a3b10f843f445e4c518845dea517ba795b91ee8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7968488943d1334fb7475d8aede2aa14864369caa904f97b207b50df2c910da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e468de22fefbc9b51274d707874100af970efb96b99699d618e27a30077184b(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18fd81aeb2565e470cd54e1852540a156b600d994f43f9504f859c693f097de6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24bb6c29f8c93f29bac732a754dc39bc4917d8ffae142d5e5550981983a9c607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a33176ebeb01b06e2dc9b6ed97def2da3e6dabd5818a8f26834a7b8e3ceed811(
    *,
    apply_policy_default_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale: typing.Optional[typing.Union[PipelineClusterAutoscale, typing.Dict[builtins.str, typing.Any]]] = None,
    aws_attributes: typing.Optional[typing.Union[PipelineClusterAwsAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_attributes: typing.Optional[typing.Union[PipelineClusterAzureAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_log_conf: typing.Optional[typing.Union[PipelineClusterClusterLogConf, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    driver_instance_pool_id: typing.Optional[builtins.str] = None,
    driver_node_type_id: typing.Optional[builtins.str] = None,
    enable_local_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gcp_attributes: typing.Optional[typing.Union[PipelineClusterGcpAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    init_scripts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineClusterInitScripts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_pool_id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    node_type_id: typing.Optional[builtins.str] = None,
    num_workers: typing.Optional[jsii.Number] = None,
    policy_id: typing.Optional[builtins.str] = None,
    spark_conf: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    spark_env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ssh_public_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce9dbede4bc9a58022da5c6666000951606d7469efb5f28c295854e1e8fd39f(
    *,
    max_workers: jsii.Number,
    min_workers: jsii.Number,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fe15f6c1a9249712f05e440ce11e0b30acac9602246d78f80ba0758db838184(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1de2e1df5ff136f8a6f63727b1d9c1fb15458f0b18f73b66b7110113b77c6f34(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee74f8f8c5c1d7fd5f4b9519da168cd76d4c3f3d3e46252648b51cfd42b1b0b8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2490e45c321bce5143fc9469797d25aad3f55427c63792136e67ba3841f1b72d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f6a54e5864a25d6af8b60f500df02f15b14660f82002791aac4b6c303729f0(
    value: typing.Optional[PipelineClusterAutoscale],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7af026888b5f18b35e61519c1f99736e7f97b6cb88e4e5da33bff53a960954b8(
    *,
    availability: typing.Optional[builtins.str] = None,
    ebs_volume_count: typing.Optional[jsii.Number] = None,
    ebs_volume_iops: typing.Optional[jsii.Number] = None,
    ebs_volume_size: typing.Optional[jsii.Number] = None,
    ebs_volume_throughput: typing.Optional[jsii.Number] = None,
    ebs_volume_type: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    spot_bid_price_percent: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__034af8c7fa271cf66adfc33f002ac3ee09bbea29825a7a8a2647deff6dbb65cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b50743b0d980404218c560ac09acfaffed33d1c6ccd6ad9da71214f7bc9d908(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37387d1544fb8e3dbf449aebbaa72791266b980f0562f25f5b05006f984ec526(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aedfb19135ad615868146bf69fba2d2d0910c26664440948c47548851bfdd5f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dae3879597c52418887e3550f959a7acb3bc5c668705591b1eaa3eee00e4277e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a48c57fd175b08a2aeb463136fab3c209164b185d54afdf43c27758c3c37502(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b40173b02b1a8c511dcfbc4fa2513d972ea31a77a5e6eb4c2cb90c05dda9a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e32f3a85628d46feaeb90af7b67ee0b258dd99c2fcab6cd79bed11f0b4b938f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__277411d5e8b44aa476e27b98f9c3930880135294b36118d3e1416d3b4e9681d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51a35bc8b068430d974cbdf4d55b6a7861e4bef5c158f0970c23240a16453a72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9bab925d3a74619b9a4b087b1f7809fc08d20aad58cb31ed7281b64fb6bd6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67052b274b614fdd8ff2840e90fd0d7a48e9a5f9470d24c72a7b1fd4f96631c3(
    value: typing.Optional[PipelineClusterAwsAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09db73fe322631947c9826880885b081d3e940872effb957617546e6ee0a0d46(
    *,
    availability: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    log_analytics_info: typing.Optional[typing.Union[PipelineClusterAzureAttributesLogAnalyticsInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_bid_max_price: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afefa7827dfb374f9f885354a0b343abf0cc7cead55481375fbfa8cd08318b92(
    *,
    log_analytics_primary_key: typing.Optional[builtins.str] = None,
    log_analytics_workspace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa16f341bb160d1bbb48d01a8357201c95db864e1b194b8871dc809460f784e2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d9087909d34e3c2226d0972f4cd76b90fa0a04da8dbb8ce825070c727d48e5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef71a8a50b41cfd85b233c56bd8c93bc1972d5fbbdbae55e82bfea741f4c5faa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd522fade832d0bb384e8757a6a40ee442ac74771d3bd211e4f42a57d89c6e1(
    value: typing.Optional[PipelineClusterAzureAttributesLogAnalyticsInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51364aa45ea420fb8b9c47d02ef8d6aea243db86d51ad38d128bcfc4d46ec26d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6deaf78af2052e90547146e612e964cbf9d69f3f06e2138233a63c69365fd643(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77b9cb2951bd82daa4adf7365a6017d47d9a8eaab7a7543741c41374cb91e86f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dffe0a39f86ee95c49dd36e8c2f362709827f1996521fa8af5a82fb475c9d23c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3281128a46c79bcb7d3db67dc3d6665e954f411e21cbc4bdbe0c6ba486d2fe1c(
    value: typing.Optional[PipelineClusterAzureAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdae64159d2d4575c3ac781cbce96f2254c0e060d4424a3ccb2b7fc8517509ae(
    *,
    dbfs: typing.Optional[typing.Union[PipelineClusterClusterLogConfDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[PipelineClusterClusterLogConfS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[PipelineClusterClusterLogConfVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79c754560b803a4ed489c688433906f7b8250a6e1f2694e35934e024fa375f07(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dfc342752bd16830b28a56b50b1bb61f39209662af4c6d1e91ad5adbfaf2c4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b53c6c3f82ebf7e3fbe7d31a6dccb41352abca30fc763ed1e1a2a7c19363e262(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fc9f865a104a1f27a96d3d66e17cc8a72925c203a7cc009ea0d8698f1dcece6(
    value: typing.Optional[PipelineClusterClusterLogConfDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad27a78ca71664a0e32853ca8b6b3a51eceb93dd4dce71303cbd3b246a8e4ea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e6d68c3bc3a9e8d7c64137a82f6463564fe8d3791b8cafac3b26f9bd953a6e(
    value: typing.Optional[PipelineClusterClusterLogConf],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fec978197dc868cbe45df928a2d5427576192a929c3b00a61f7e5edc7af2d44(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc7cb8fe5a0fd58e17ae409bf69c4646d59dda0df1d864ad7a72fd90c517adae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a31d1241d7f8f609a6ef5a382f16522098525df752b68cf1868e4ddbd75241(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63a09afb8148ba93a8e2c12adf938bd1dfa4cac1c2da2d66fbde7d9b5bcf72af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e07070e38bf0266faa6c18548919fc882c6e4d5fa1df021c6b73fb5e377c119(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc46bd2b8f68fcaa82a11a2e05523f59b6345b4c5fec20c9c7a49d0e559384f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aeabb05479bc828373b47bdea1405e6a69e6a724b04e8ba93232bad5ca963fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__683832da4aba9347cb5750987bb4ef264764efb3d01620167644c18ea591b74b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__695465dc2be754fbd2e05a184c8487266b265af299ca7b6b13327cf4caf1ff93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f58f1cdd11eae849fb94989e6b66c7e7a4cebceff8c52d310318bb10f4736679(
    value: typing.Optional[PipelineClusterClusterLogConfS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__042fb7e8d8e1065b150883eaf40acbc92e36a6ca366a8d658b03d45d7b44a99b(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ddbb72fff1a48b044e3b0b05d5ec0a3965e6caf472691f3cce6675143290e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a86987bdb43a8311ed9e512f4c8d5e0a219d17045dce1535fd443ad2d6f5fa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9645be08c560333683e2e7b35a7d635c5692ddb9cbe074f8333a4492fa975a36(
    value: typing.Optional[PipelineClusterClusterLogConfVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b710373a181627bd2598489140676a7d69d36adfe98c520af7e0e3d394c3f0f5(
    *,
    availability: typing.Optional[builtins.str] = None,
    first_on_demand: typing.Optional[jsii.Number] = None,
    google_service_account: typing.Optional[builtins.str] = None,
    local_ssd_count: typing.Optional[jsii.Number] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__592209e8eed1f04fcad13ceba385289a14b46ea300f3529d3fe46916c2e3336a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccfb66e1048f88ad8ae8b81fb2cc1030de5f2dc3ffde38da0ef080caf2358bea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c2dd36ea6ca4657d2b814a407283fac06f027f13850cee388c221033c0c7f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc6db22f54dbae2c8bfa0e6de14dc2f6636312e44f4bc7d2f9d2f42962b56570(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d6221c0bc0eadb022d9386f12e2ad44cc8a87677616c4bc1300b406f6413d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3ae1f293d1c69e590a0befd3409e1af4349116c4e9949edaf56a4f7dde5af9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__426feba19e4b7f80d3d89b2ef788d55e1b23568cc54c9aeacbf28ff62b855dad(
    value: typing.Optional[PipelineClusterGcpAttributes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9606725d916bb4025b10a7e8de1a9bb8400329fca569201ea64471d72b11ca82(
    *,
    abfss: typing.Optional[typing.Union[PipelineClusterInitScriptsAbfss, typing.Dict[builtins.str, typing.Any]]] = None,
    dbfs: typing.Optional[typing.Union[PipelineClusterInitScriptsDbfs, typing.Dict[builtins.str, typing.Any]]] = None,
    file: typing.Optional[typing.Union[PipelineClusterInitScriptsFile, typing.Dict[builtins.str, typing.Any]]] = None,
    gcs: typing.Optional[typing.Union[PipelineClusterInitScriptsGcs, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[PipelineClusterInitScriptsS3, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Union[PipelineClusterInitScriptsVolumes, typing.Dict[builtins.str, typing.Any]]] = None,
    workspace: typing.Optional[typing.Union[PipelineClusterInitScriptsWorkspace, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e93df7a4b4e85a178aafddec8b8444061a67acc0158965c9fbc3ffdec7e08dad(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1a2169d341d9a1b54e145ac37e34b8b90952d5a89733fda8e2709d66f2594b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0804e0ac900175e8a31d52a0e43c9fdc97540c631bda3bac9dbbebcbac386417(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2c7564878391e77e1ecb1813e9874fd80e410473364e40578f1cc072d990fec(
    value: typing.Optional[PipelineClusterInitScriptsAbfss],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773d8055d11a750f72b3f99d5f7733d209001918686e8dcc5a50db3d17f930b1(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78827de0293eb00ad644174368fd942beadb0d575beb795330e3862bb3d1b95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1467dfd18b63ed1c69984b6de6b8ce9f8c3c3ab74726298318a3f058704f769f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f9edcb9e850114867de2f6ee074dde5259a6471e37f4e4e584aeec2a540300(
    value: typing.Optional[PipelineClusterInitScriptsDbfs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6fd7dc19949d16fec90ab1a0ff7e085302b16993a48869f0937d270c22015b7(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__701886f366bcab6170c3bd2394fc427805182567a9fdfdd32c2aa09b6dc0f0f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bfea21e750306c5b21603223837912010c380ae90b7df3466b885c784955173(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5007b948901d62e9d63d21638cde663252a03b024cb433830cc9ab209099d26(
    value: typing.Optional[PipelineClusterInitScriptsFile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30819dbed6df23b53891b67db4dce91d1e68aebb8b25f3ab57511c55606c72a3(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d21302844a476d5838e4e296a138354123b06c50d1cb6b0e70d524e468abce93(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__949518cb359e176b60a494e19d76e6396a08020e77808e52f993443f1e6a132c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8330567bbc43ad983641908cf4a97440f3d16d09c224be7c9ecfbd5658a9b9f7(
    value: typing.Optional[PipelineClusterInitScriptsGcs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879fac48a3d2b2371b4586c591c212b08ab4682f869eabc73441135e7b32d798(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1809a156de53f72403132d5a340b04299149cba61a7e75a73765f6fb36d36505(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f49650ee13adfbdb2d603e541f611196b928ecdb2be39caa61326c592ae123(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6abd859892e7b5393262d0559d4bb68a54b9473912df0611d2077219bf7850a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02229def7288e4c942fa5346afafdc85ac80f9dd7ee03198e919889e4ce2d231(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d62682f2e79cf083bbc5824c1155d3e621e4003798cf73e1c3229a20e12fb7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineClusterInitScripts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a844dab2df04ef50ff41322260f02051dca754ee9dd06dba4792fdde06f92f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27ac8fca519ed0fcea396a2ec6613ec1ba834ef4cd46a535468c6386ba4a8bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineClusterInitScripts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2045e73bbb4999b3222f9ed41e0b08c4ec5686ca7807cf426616d71db8ae44f8(
    *,
    destination: builtins.str,
    canned_acl: typing.Optional[builtins.str] = None,
    enable_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_type: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8db4af9da6a51f8e4ffbc84afda9627a9ec02930ef26256f67e1f8bb8b0014ba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45de8c1834d4b16a41b09c1548a9c9ce0fe7be5ead905653869a0d10aa972c15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dc9f8cedd2d53468f49658fd2487abe0b5fb9cdd2aab571474bb6accc5b4871(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a7a77c34aada88dc679f75ed0a0297fb6a482b369330560d8684481ff92621d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__843e85deae8b66607c2486c93edd7c99b48fcf401748b3598b427b27de555f05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0faa7a03216b2933a7fb25039c083b71bfa404c8e4e44aee1d820b6c89d608f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6306b195cbf041ad83e6e5c1a42e0f6828eeed3d597954793422883419a7eaad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__139e883bc023de2afca0288b96704b37662fc11767b1613f8388ad54812572f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6547b1abae046c7250fd7f2e0891d476789b6eee05d869243b1811198525b7(
    value: typing.Optional[PipelineClusterInitScriptsS3],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e2ac50bd3ed45f5790abb81df5757f39746eb8588abb487c931408ef401f3b(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6429efd050eca9fe8e4e24287719a27cb795f2cdc1c24feeff42a0db386792e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7413a0a395a01837c5fc91f95da0310683f07665a3a508a3358a9b543191e9ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ec2f7ef6eb7e69a434441eaaf8a372464617aecf972ec865d01ef6cc784b04(
    value: typing.Optional[PipelineClusterInitScriptsVolumes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3075f0ce66fa7869601bb651bec348c898120755aed86f2b322985c6508a76e0(
    *,
    destination: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2860bf0abc4996f8888cab5b15660198fd769fc8a24047706a48bf064182db0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd89e07da7d3805379507e8700987ace948bf9e0882cb3241a935ae10f8caf15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c333e2ea596dd4ce3be82fabccf3c7186aa2444c106dc8ccad66b50cb32b88ef(
    value: typing.Optional[PipelineClusterInitScriptsWorkspace],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b6853e27ebc950e9ebfbdc65a2671e90f8ee99067592d8c545a59e96206f64b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996df806c4a3a7163cea3aaef61a4d888356d399d5b03946300dfcd829841055(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b33a40ebfcfb0a454d6b6df420e22a3487fe6662e19511f0f38f0aa57e87337(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0906c1235da71a2dc07c438f07c59ad86868ac130b0d90832afd037c529fb320(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c725476ac49792590c40a2ecf7a838d852aa7deab25c5125452f647f1e8a599e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aee7af843d919a00edf74f64b2360f55fe40a73abc4ad08072efc7c8d3bbb127(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineCluster]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68f686b393542f758490bfc53c92a41e454b4a54842f9409c872e10216c9ee3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ccde33b89ee7e4184a4d72ec46e68fc045fd1aa55f6309fddb669ec4e34d73d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineClusterInitScripts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631830709b6db135caab7afb66fa8cfa512a3adb3002d6b2885a866c05aaf90e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807b1063c49427b28ed2a87a22209ee99f388bd621f8725f74ee66501892a570(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec550f62fe53d73b084a3dac8d01b1c4704347f726d8525bfa7103ac6046c17d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e3bb153e66bb090fc1c785e03e5d4406a79f703343bbcd503a7d7f1dfc3064(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5214bd08eeb09f4bf7f9ace89a5fd920379dfad9efdd8a8fb02f43a36bdba08(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2bfbf599ab5a89b240ba478d5b474bdd9d639d94bfc1abecf633f8ab0a5e25b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52daa4d5938a16e79cc53deec1d3e87502543fbaa68a03ca7b56b682841cbf12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9c10516fe628ee18399e140f2142998675c7303a3628e4bc2b6c7a699d06fe2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27e3cb5b1eea5fcb04ad12e214ddc57eeaf315bdbf01c057b730a5807f544a62(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc63ce4e08ad091fd56b6522e12937aa41cb6e21e2dbd4625562209d77957e5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36ebca77bd76b747421301a8aafb76338163ff991bb705fc9d0f299acdd86880(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41923d2695e88c6400bf0c524b59737b508ea8f39b0ee8ef8486a2a6183b7811(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f18d3841371804c5d8e8656801444d8fe3d2de21ec7023db7692ffbfc1e954b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e41b430d976be56ffd57e79d96020dccc7707ca5072ff19eba520320cea75c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineCluster]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6187572c5ad940dfd5a25a138b6dd12be1d616cdc158bddc0762499407f2b92a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allow_duplicate_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    budget_policy_id: typing.Optional[builtins.str] = None,
    catalog: typing.Optional[builtins.str] = None,
    cause: typing.Optional[builtins.str] = None,
    channel: typing.Optional[builtins.str] = None,
    cluster: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineCluster, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    configuration: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    continuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    creator_user_name: typing.Optional[builtins.str] = None,
    deployment: typing.Optional[typing.Union[PipelineDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    development: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    edition: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Union[PipelineEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    event_log: typing.Optional[typing.Union[PipelineEventLog, typing.Dict[builtins.str, typing.Any]]] = None,
    expected_last_modified: typing.Optional[jsii.Number] = None,
    filters: typing.Optional[typing.Union[PipelineFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    gateway_definition: typing.Optional[typing.Union[PipelineGatewayDefinition, typing.Dict[builtins.str, typing.Any]]] = None,
    health: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ingestion_definition: typing.Optional[typing.Union[PipelineIngestionDefinition, typing.Dict[builtins.str, typing.Any]]] = None,
    last_modified: typing.Optional[jsii.Number] = None,
    latest_updates: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLatestUpdates, typing.Dict[builtins.str, typing.Any]]]]] = None,
    library: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineLibrary, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineNotification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    restart_window: typing.Optional[typing.Union[PipelineRestartWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    root_path: typing.Optional[builtins.str] = None,
    run_as: typing.Optional[typing.Union[PipelineRunAs, typing.Dict[builtins.str, typing.Any]]] = None,
    run_as_user_name: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
    serverless: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    state: typing.Optional[builtins.str] = None,
    storage: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    target: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[PipelineTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    trigger: typing.Optional[typing.Union[PipelineTrigger, typing.Dict[builtins.str, typing.Any]]] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d457cf4da02af0dcea95b07a13bdf3cf3b9471e9120e11e8e9a6be9d670df7d0(
    *,
    kind: builtins.str,
    metadata_file_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bda9c79fbe2101594798ef8fc2905fdea574d0af8d9b5baebfcb16c2bd3d09d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60b68318c0559e3ae0ac60f391ab4f882350354565b31c687a3f7269e39a23d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a372a4576f1e503f599f01421bac7e56d0823d3f0a1cb24c17134930107f2b56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__120a1900efb40d496ff1b69fb79a1d6c022a6710437cefd350642a1152cb3472(
    value: typing.Optional[PipelineDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b1a3dfa0971b7c9b0a277f714540601dff9b5482131841d699c6c4a84013dc(
    *,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cce8c58d8101a6fb86b9b8c9d65b645a79a4756d84088f1c4b6e8d2d232edfbe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14051ab6e8ca902385d97b381b4396655123008e72755c704140d8f2bf262294(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cabd13e3005ef8be7802d157d2550ed58695e8edf7de5502ade42bc23330da4b(
    value: typing.Optional[PipelineEnvironment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0bdc19b18f717a6cf77b78ea815f6911b427795e0ca1fd5d5e254af21afdd1(
    *,
    name: builtins.str,
    catalog: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c0598f74fe1435002dec9c55445611b662e1d2bb4f83734d80cadae801f72cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__519e505eb78e6a0d93936ff36835b4c5b01bf8ee55e225bcccc679fa0218d18b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fdac64802addc073b7c2c7cdd62a716f9620713aad9a19f19fc4a0c37607d75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6347ff3985dd38629c6eef5e2c7cbac9d6b5cd4ab1b80ae3ef50b7a12232934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8874367918c58253277f6d41f07dd52d6e184d6b293fbc6cb7b4a68a32105947(
    value: typing.Optional[PipelineEventLog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64638efb34092d970f979aa95dda37b337a35c8d4409b1048d5fb62a1c5f7018(
    *,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    include: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0891539faccb9bce1a5c612ff798c286b2b2afb19f19cfdd0cc0c638ee14ee15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9909dfe2ca81ce429b712d30c404f46bf95aa9909c429d2ae7c7128271bac44f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__299e91eb4a5a518a5fd257ec4d46cdf8f4b82efd9ca802e8702e5cd218d95b1c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64895675f014f00616dc9ca02330c00c7475651b79bc03084118f9cc35261590(
    value: typing.Optional[PipelineFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62fdefe8d555d1f3c86cc11cfa20788f1ac8f0d0d867286c8da364fef6be9ed5(
    *,
    connection_name: builtins.str,
    gateway_storage_catalog: builtins.str,
    gateway_storage_schema: builtins.str,
    connection_id: typing.Optional[builtins.str] = None,
    gateway_storage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03d6be8612081073eaf87ab80bff24230daa9878d941a0b99735a120c0aa6d02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08fbac6aeaaee351e5939e793e11d265e61ed054dd88da275b7cbbc57b82ab69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e14d00a3cec6b23b09d220a6c19490feab5745928629a0b212df0952e41cbe85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b5e5fae784fd38aca2fdcde3b6b2e87e9b797a681c3f6172ff31a965a3e0604(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b07b7214443f4e23f4879fa4f49f49c737e55dc1c83ea14b1943826f16152ad8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d50b4aec9c1273e2523d6c78cdd5b4d31dfaee28037fac055bfb5c4eaf39384(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec2a294dd6088a2744ff373dabc7edbda043e40d820269b2d1a708b8617e8c0(
    value: typing.Optional[PipelineGatewayDefinition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe1fdce8b61ef4e74dfb9137f6efdcf51c918322211bca74faac92bc6c1d557(
    *,
    connection_name: typing.Optional[builtins.str] = None,
    ingestion_gateway_id: typing.Optional[builtins.str] = None,
    objects: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineIngestionDefinitionObjects, typing.Dict[builtins.str, typing.Any]]]]] = None,
    source_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineIngestionDefinitionSourceConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    source_type: typing.Optional[builtins.str] = None,
    table_configuration: typing.Optional[typing.Union[PipelineIngestionDefinitionTableConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265b42cd2ddb3b636903e241e8d396b9155f0377d733cc091b479ba1bf937a8c(
    *,
    report: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsReport, typing.Dict[builtins.str, typing.Any]]] = None,
    schema: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsSchema, typing.Dict[builtins.str, typing.Any]]] = None,
    table: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsTable, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81dc6b11f002d166b909f8ea967fe8084730b8c48af61b4dcd83b1de52709ef5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d4b7c685ce1a02873f60de570c7dbed108019260ed31216c18acdb7946440fd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa6de567f178301ba4950a226ee9439adce0d8e365bb46db1344821632c89b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b61b4a5aa213b74c58efd45b42e6353fb9dc310b6fee2dcb993f57c738ca223d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7a3ad75aea51f7ac0d7dac461e6c5e193cc7a464358b4cd7e4341423eef8690(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b59b7c1fda0699797b64248b5b696287f1fe2a9f9ce9b98f141dcd173be29162(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionObjects]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6eb0040d9147852bf2b6698801eb5215c22db5ff257207b587aaad0ecef4e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687ed40e742f23c98329291f62d12a608ff61d7b7618446f9ba27204f6ebccb8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionObjects]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d780f9caccab1364ee4a86d0e87f1b5b0392946aaacdb617420e52613e2cf7ef(
    *,
    destination_catalog: builtins.str,
    destination_schema: builtins.str,
    source_url: builtins.str,
    destination_table: typing.Optional[builtins.str] = None,
    table_configuration: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsReportTableConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca2d7dc70c762115d0b0421ee4261199e2de1aa8d0c6983f61fae48f51a0abd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a14d2cc134bc361bb756c6bbe91ecb8ae5a80397b22871e03b69411946a5f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b1fc2d185c744ff1f12d6aa06cfb723e4a987b61fa3705e8e74029f01e82607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072ca0cddccaaff2ecc9b5e236d51512648b2ab7378e0d55e05c92ce04835528(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afc6316a3fc3cba550f257e77786bf1cc0099904b058be0da466f51e568571e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b45d886fc6f34d41facbcc89ace49119892546938fae14c51c6211471da298(
    value: typing.Optional[PipelineIngestionDefinitionObjectsReport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2ae4cecf709d650d294c4de42738d039f3c89709ca82224e454e920a8b22675(
    *,
    exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_based_connector_config: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scd_type: typing.Optional[builtins.str] = None,
    sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057156336f7490bd1ecfc4cc3e83b20fa525ee8fb7cbc716554536d9232f277e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b85125af5ae84291015caa19d2d70ffd2c41ec69e4d7cd4cda15478324d2aed(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e64bfb064a59d59b998a543b25b9724822a9342c0faa2d5c85bce1d5a47edec(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc0d3e609859c341e5448a20f1bcd1ba5d140114dedb0e13ee67e04415511122(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af8663b2f1a8b931b76a65454814ef96a7f0b1f83c7dca646514da924399ef96(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bf4aa3a3e3674c180e165c0b9bd7d260721d76c3998db5415f65b4ff2131cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05e7f53fa4849fbe677fd07802d6fa2656393f42014bd4358617784abc7a832(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59951f71b7b156efc2f322ece1654be2de818ccae8cd357343d5253e71b64ad9(
    value: typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d0a4f8df42bfadcb83acd828b9d2a3f407fb9db1f136ae3d88e69f7952931df(
    *,
    cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    deletion_condition: typing.Optional[builtins.str] = None,
    hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b7a52353fa3306466481af3ed3c97a9b4ca6413ff1f584f6fabadfeb5016e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd609ae7fc8fc682e209eaaaa45bffc9a3cbd46976db6f34eed5cf2cb9e0a94b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fbe7eece88d07a0bd67dc07f4f9bc36811b422d0c3ad1c79ea1ef3c4ba11959(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd344f08ae839384697ce74540d9bebdbe62d9b2aee955af34c06d776c4dba70(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff25d40da20a3f58ea5e51f8c90d47a1ec152d32ac86c30a1df190e839264cd9(
    value: typing.Optional[PipelineIngestionDefinitionObjectsReportTableConfigurationQueryBasedConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fe20da001a233e3a8756b14c8a4c5bfb7f2367387dc5107112e1377a7cd0462(
    *,
    destination_catalog: builtins.str,
    destination_schema: builtins.str,
    source_schema: builtins.str,
    source_catalog: typing.Optional[builtins.str] = None,
    table_configuration: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsSchemaTableConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b6cc34b90f1b782407f1bd7c087dbc9662582fbfb946f7885c5b4402cc5fbf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__166df458d3e3e108e5c8f13f098c782c0dd36d2cf1ef770a60ea61a5cc6ab7e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4222685dc3e0896c806c24c7fea472c740d06bf1bd3c407844507de4d2b9595(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__859b9d014282744993eb944326d222cb9e8876d1e752dab712bb3d7d535061bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc938d897a140918143b6060519c2c82dd1187086c8f384a35ae0d77956580e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3915f38ecf78a782afd41a1b6d39460795cabf8ff616cb27274c9e1188448158(
    value: typing.Optional[PipelineIngestionDefinitionObjectsSchema],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fcf3e521518df575b9b150372e2548bcf992d0e7f92af77f065e46ba5a2f387(
    *,
    exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_based_connector_config: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scd_type: typing.Optional[builtins.str] = None,
    sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd089ba50d2270e16c7c62044c5621d697e9c7f11de4ef45a3bafa11e482c453(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25408907137cfa926475507824c9998d7292682ef12e9251b1d7943309df5236(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a0d11f22edc84413508431d68c111bd7ce27367d321987c2bc0a624fafed4c7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135457dcdb8e7279bd6fec6aac1b0025cdce30d96b75babe0be75563ed677d1e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b92212d2fb8f06398e84258ecf0fbd3e6f37d32dcf71aa668b1eff96ab7212b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36bb9d050ab634dfa52ed9bed774bce23dc50a0467a3361780eca51d09c3c6fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3afe8917b117ffe1c320819f5c5917ba165c70dbfa617b6f3107ebe397e7e1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8a5ef3b233c9c68c0d07ab14db0b0ad42d6c452472b373e55f3e3f1910eb60(
    value: typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296b9cf1b2a31c16d55935e577fe59245a9e11a5fb337afb5533f5c0b0e22def(
    *,
    cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    deletion_condition: typing.Optional[builtins.str] = None,
    hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f89cba9bf9f5c9ccde116037836e8c8a2a80d9d9822aac65f143c4b11aa4d39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ab98bb6ce2c1f2192fe451a438aea77f716c957f406a54e846570e328f26a6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6675002bfff6d8b054478147e8f1bc6bd17a52e2410f60e5a1e6b6a0925fdbf1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07552a408da7cd70d7e806728d7936314af1da0430a021c947c9cda6e3cf11d7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e40aaed1140283544c9f8caf7f33fb6dc7e7c76e3a25162a3d7dd4edde2053eb(
    value: typing.Optional[PipelineIngestionDefinitionObjectsSchemaTableConfigurationQueryBasedConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41170ca88768dfdba38616c64eab02a05ad0c69e72f3378af4ab3cc71db2f2f4(
    *,
    destination_catalog: builtins.str,
    destination_schema: builtins.str,
    source_table: builtins.str,
    destination_table: typing.Optional[builtins.str] = None,
    source_catalog: typing.Optional[builtins.str] = None,
    source_schema: typing.Optional[builtins.str] = None,
    table_configuration: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsTableTableConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab453a20e815d0c840141b1a26a427331132f583ba986ec34070c31de4dfc048(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c6a07bff158bdf73aadeefce07a22e813b5ca53cbf528b3fd9d96774e2fba6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187de915cd3b0e84ed631cf79806f114c272c753dcb5455e7aeb0fbb1544dde1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a33667d9c4524627c26d26590637d56be8330788a91987efd95ce222a8c4a7d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d6dc3baa2cf15eda1457f434cf46547bf8cadc0398c8203c7303a25f35c2f62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf296f1abe222661e4a2d027a55a5c7e2e0b4db22e288fcca1162d0270238dc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78d026e1b50dca8dd6f362a47ca6297e30ff9354d8e2ef23acee6559e5ac7023(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6eb1308f00a94b49033cea6615bdab9ef0e5d90145c6546d872c24349d00d3e(
    value: typing.Optional[PipelineIngestionDefinitionObjectsTable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f3f8af5ec97a7ec34117bd984ed510996aa072861e70bacebfb046379de3fbb(
    *,
    exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_based_connector_config: typing.Optional[typing.Union[PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scd_type: typing.Optional[builtins.str] = None,
    sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c14783407d6ff9e3e94e7c463e5aaa88660d4dd13e2366fc35a9d4eef920a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e93fea143d8c0f054b208d4f7367a4549a9c9ea35d706e2bbe20ec84d7ef55(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0166ca2f47d0c918ae84f69ae907a89847647219ff33a325246882916f21487c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8031a5f88964aadd82e92db61ca0f5159360dedc779338c2e35c59c08345768c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7a5ea75cb58414c7f9a9fb1d0bb4e01d9811188231d8f9e52dc16b0338bf18(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddac130d835315919e4341ac75f4ed1a66fa6d31eedc071153c296fda26061f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3513bbf0f7d3e5c7b214b9b5edd2ce11262cf686a1c2980c20b96670a11cc980(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d335360687b4ab8d4316098cfa1aa20a6a0f11ce6e38699ef40670848aa5534f(
    value: typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be35be9b12dccdc8bd6b1ad5d15fb46ba2c7fe961ce9159afc07a63ece579e2(
    *,
    cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    deletion_condition: typing.Optional[builtins.str] = None,
    hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f74725d58f1f1200f95dd99cc67980c23d659dc0823409ad2816bed17c2d0f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8619547a6d03daec320c988791150abb368ca32abf72cb3f1eefb8f5255fb7f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f48d1308d12285b1a81adc4eaae1fdcdd0e4a83c78824d9e151e50e4182dafc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4683bc644624250dcec5d5254cf690fbbf0ce17af339307477962078bf993257(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3658ac6add6bfdc47fb10c708e9e63ca04d74fc15802ff1da6fe84406ec1627d(
    value: typing.Optional[PipelineIngestionDefinitionObjectsTableTableConfigurationQueryBasedConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c390900a16391ecf82e8f1c1b0e0d73ffbb21fd66ab90b52492b72dd10fd54bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c89b6db6167bd191775e820a6421e12c555eaa68afd0a34bfbd110b59c3346dc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineIngestionDefinitionObjects, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__417a3b4089c58d12309ffea6fbb1e389a7496fab625ee9f8ca208e3f2fb54937(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PipelineIngestionDefinitionSourceConfigurations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ae1f384733d20a9e8d0703916c34185e19cfea0987aaf02ced0124881894399(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5476e64786101bb6cb7caaceec5dda14b7250ce30cf30b66812f46d8e94f6200(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01c20f5c899556d70f3980cb1345155e7b8f9706f773f1113a57daf295f0379b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4583a74d96f1c18f22b33ff17c9b114efdaea3898d7c7f126ed328bec9069f5(
    value: typing.Optional[PipelineIngestionDefinition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b148d879e110577523487452fbe5744c5746698c26c7ce1095cc368f3600f28c(
    *,
    catalog: typing.Optional[typing.Union[PipelineIngestionDefinitionSourceConfigurationsCatalog, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__087bf8c8f4d2e8c89ea335992b6dd2e3a3d9d99bd1ea065071be7ff0a5ec629d(
    *,
    postgres: typing.Optional[typing.Union[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres, typing.Dict[builtins.str, typing.Any]]] = None,
    source_catalog: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca7d03bb9f9d707168800a509389dd7361117b219da952f6a3363276ac785c55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b68df714e611a493a84d849f0a2659568ee556ed2dc37590220cda884857140b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__767fe44d037f5dabc5706011f1e4ffb86d2a5de88176e060d4f30b42d772ef93(
    value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad81892acff8d987eafc1de2e13c03142b66d10aaad20247afeee353f3e6cbc(
    *,
    slot_config: typing.Optional[typing.Union[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffdb494680107f7a9d8268f128cca53a6636192142c4635436ad4625c3696767(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1554139a74c7bfaf4c7140c015425bb9e82bbebee34957dab960797458e750e8(
    value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgres],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__019e7ab6182fd2c9605b97d9ab29d06c8946e8d2a157330d1ef28b78ac6a9a8f(
    *,
    publication_name: typing.Optional[builtins.str] = None,
    slot_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__648832be68b3cb80429f6812b4769cae59351988601de7dc13a3a7a79267c57b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4316d5a05a6956b944474d8a63e344987f37f08eb69d58632500205abb5afd59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c61f139de71b86272307e382a54bd22a127e391c0dcfb86f2c1a4b3fa3f1aa2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8803c7987bfea8ada46e49e35a4fa8c228f078b10811501e760382ac77a741d5(
    value: typing.Optional[PipelineIngestionDefinitionSourceConfigurationsCatalogPostgresSlotConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__936b98b40514dc1ce2561a4632222043304cd4ffb2818b777e05df3e81a591ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__733d71c11dd2926dc5cae8ed7248cc1abc70353b828696f190dc1b6aee88632d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ce134b945d30c4e632603a7f8fa52a04db532ccff74738a297376bf69185cd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b018fb30c77f9f947fe192f2a6eb5449a5402e177ee268171608d62d28ae00be(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a0910b832b429670694c9216c21acf76154d52bef7cce1d3ab05962717c793a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__967d7b7538fb9aaa9bc4ec918f308dec0292f0a29025bf2218932722a96ca25e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineIngestionDefinitionSourceConfigurations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bf290952e2e3d8d073bd1ce533f03d305e3572fbb845e60ab0ee4899bc6b9de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4503d4875e92373d8c3dd03f954651574d43ba86a96d840063a8e5aebba5a36(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineIngestionDefinitionSourceConfigurations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79880d315425bc50cc65ac0ae6f469045fbb3b6259a93a1cd6a4b5e3ab3f4f3f(
    *,
    exclude_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    primary_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    query_based_connector_config: typing.Optional[typing.Union[PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    salesforce_include_formula_fields: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    scd_type: typing.Optional[builtins.str] = None,
    sequence_by: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d04b1380d31ab94e68427dbf5cb9b5727a8f988d41b1e1fb73763e7da95f0ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eee803e975a786c79c28b9960a593a1a6a24e915e5e4bd4df0170e885d79c0a5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bab630325de7ecfc139867673898c80d9c061bc356f743436b3d53eba36725c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a1fe7bed1f8d6fed4284a92c0c50cb33266e75caa4da6cf8f0545da142d8ca(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f8ebb784c683b044796608868e882b151112d1a39412cfff5fc75969dcfb654(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a1a54ae47ceeb0b1ef80717d4760a8ece661defe859be04403207a2cb814b54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d1f72f7cfaeb31938144ee39d748622a39acb6e8929b9e027d5cdcb304c009(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceaa0be954ba78f4a43b121644f22178ad0732c6fc98a893c77c64e0a951b674(
    value: typing.Optional[PipelineIngestionDefinitionTableConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__667591fa5f7ce9446962be5fc0664ba899a7c109078194d21892236b5780f510(
    *,
    cursor_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    deletion_condition: typing.Optional[builtins.str] = None,
    hard_deletion_sync_min_interval_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e403a9c507163806e65d55a2eb9774f928b42f267f07fd17f03b330cb6952dc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a25817a7c165bd2363f4b3ec8a2ea765130dc0ff4c122edaaf98af778d4056a6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ad2195077e75f4098c5c6d9f8257b625f5c5b926d8d1c411440a567fe1024b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f1e4e35d81147ec9abc08bd5939cfeccecc34dfd1d35d15342ea30fb958ee6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4af82f34c4da66ee6358f538caa92262b0848b1e33857209f354a27c9e42bef(
    value: typing.Optional[PipelineIngestionDefinitionTableConfigurationQueryBasedConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__895aae5df6cd73f482c61408bb3ca47b2bf12088f0accf06db90715bb3539c8a(
    *,
    creation_time: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    update_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a502ea6ca2085c438b87cd238aa8335953e4eb733b8819050db91b7d926d33cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b810beaf2d9514b98e51d4fee615d4fa8c9df31a6211320ab384b3eb6eb941(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc71ec804cd6102f1cd12fedf8dd3df5fe52265b9911acf0ee8f4c8b23a5e59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b2f5172dfaf37353fc605f9f23bd9d80ba915a6d5c16b725c3c695c3c07edf1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc213ffcaaecd3e4d2b0d037f622466a6125feee82db09ff7193b2965a9f93ee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab1f6014a1e99b27a5f516ed45905943653cb0c47b8ec93a34130410fa34819(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLatestUpdates]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e925ea5ca6cfd9fbb5cd3f3d74e64dc1f9ad1df7bca25490fed9eec6b201409(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2365643e61047b21119ca58a72b91c7800089c583d7d7ce5f1e06a59043c979f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d199bc209c288b5c26926ce24c9fca9b55578a4fbefd9b54312e33b8954d7c03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0639c76f02a7ac5ac6cb9d981bfe795dea55fe3c0a413a39cb421426221cadba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71db015f94aaec17d87a59229595e4d8c87183f286fa4dd7c0aaef2845f9a685(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLatestUpdates]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1560db388e699f602e6ac52c25d07e99ae4739291fccfdd3ef0f687168e8ba0e(
    *,
    file: typing.Optional[typing.Union[PipelineLibraryFile, typing.Dict[builtins.str, typing.Any]]] = None,
    glob: typing.Optional[typing.Union[PipelineLibraryGlob, typing.Dict[builtins.str, typing.Any]]] = None,
    jar: typing.Optional[builtins.str] = None,
    maven: typing.Optional[typing.Union[PipelineLibraryMaven, typing.Dict[builtins.str, typing.Any]]] = None,
    notebook: typing.Optional[typing.Union[PipelineLibraryNotebook, typing.Dict[builtins.str, typing.Any]]] = None,
    whl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__192b1582e89a77558f7d2a75c84672b81c976174fc27c8e72ef11a9eb19e340b(
    *,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf2ec7f1ace1c0d2ec678e0e65e01cab49bd5975158d18d0bf9b4ec34037109(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40672a15b893cc08dc69580e935a86c0104348b94492b8638d3a2a65f656b803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0fdb0532d4df5702ddcab16ef42facf114a6452ccbf62d805c661515cbea490(
    value: typing.Optional[PipelineLibraryFile],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fadec0c6764a42b3d1e76418517426982ccaa020cdbf48a9dd760fa15eb6edf(
    *,
    include: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdccffd865df5823621a5b99f1ce81860d6cf509d4dc3dedce20668908d720e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3ef50f795b455e937c2e5ebbea0713410574ce5f003eae1ac1de2fa8b3606fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842e1a3bea8fbc34c854bb8f3b066e3bd78902179a4b422b751712b189d48216(
    value: typing.Optional[PipelineLibraryGlob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2a34acb76d8cd2be5799f8197c24a91a9c058cf0892e0c1b95624ebd82ea827(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8fae7c549a6fe248c9ea15add8d076fa7d0ab5da97065b2eb32978e5da17135(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88ef3f0dae6ba61576eb56c990d211faeff9c36d337f212c3a2978e674cb2e54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02cfb6a77773185cc2b602c7d4ce629a92a23d34578db120afec6e87eec4e44(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81557bf514c98f27c1b18f480bd80030803111d0839da4da3ea0df6e719412e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__941b428873e6206e24d64787e0d7fa0e7270b773f845a0d4257899f99088afb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineLibrary]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9762510eb02d8bbbd37281914c774f22bfee1e1ed949ea55fff9b25c52f854e(
    *,
    coordinates: builtins.str,
    exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    repo: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39bba964e08c67dc8a4f2ec6d7d2fcbe1f65158087cdf4c528ef2efd1d2cb0ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1402f8c23a02f838e6aeb7a940d807ccd0df50604e2741cf15196de2428ff377(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0207077b5abe91b53c1a981032064b7b4d91f084db71e9bc6da546e896c32cc7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f3146760112fefb2bd67fcfa97a81ecf9a00613ce6a2ee488d5b951c17f8be0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8511b3696b259df3391b274a544f46e94af97b8b8e09fd3d7dd1a79db7f8f82(
    value: typing.Optional[PipelineLibraryMaven],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc8590d33fb32f1842216fa9e717031b1dc856c5fa176183fff2199431d6a380(
    *,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd01d3abdeef70a00f986c4df9c71bb53ac71bed2f6d99bdcfd737708d2cd83(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24326d322804cb172a6c36232fc5a8c14d356d7aa70ed84c1638fe51befac8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817625d545c00883dba62ebec6721f41c983682d781d9a73349430f24f35434e(
    value: typing.Optional[PipelineLibraryNotebook],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47584481f20b041090a41d476358cfb193b50b8ed354784137955510a7635938(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a45e844c8624b48e6b9e2a60ee9a158a18e404859e4c00ba84f3a9af395c79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5ff5ad10a76fd765c1b4ab99c5fa0fb489a1501d5f98a8c69323110f970831b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f0f1330ccdcf68d22a72400fa4519013bc5e812b68193fc914bd4dd07ec9666(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineLibrary]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b8e401d03bcfbc10097c2395af05aff23ca1cdc689241b820c76ab6b8761602(
    *,
    alerts: typing.Optional[typing.Sequence[builtins.str]] = None,
    email_recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6aca95e7ece8bb109cea2c71e613419108b1ca2886cc42d59674f1f36bc21b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a66e961227762c7b182c9167aa04f72f9bd31331e0546df3097c01a6a9e1a1d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8231cd11af95102a530318792ce0d1f23673fe1b9f2c164179a6a7b213f0d414(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b85bacc1230974e08767a382bfae3194c400bdba21bbcdfcc7961c2c9e18fbb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea7d09f0bf3cf787a07796959ed668f6733c8814a8d24b420f9a0c74824dcd65(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af3a27adbe8aabb5143af173954cd2b3ef3b906a41312c354837028a5734b82(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PipelineNotification]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ad8747597828880f5cc8bc2efb25caa1ad683dc883428c18e99c410d461235(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9054580b8a926c4b33655825efa87cdc724a30db1aeff0f21bc77a07cd3fc07a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__645b1e294b1de53b2f2eed598bd13922919608f76b48c84659597180c183c479(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86723a1b41e3e00a1f3746f7e6f6c1aa26853ff57701cd2b6c95dc6f94412ffc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineNotification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eae16d3e94207d57131a361eaafa4b5539358d6ebdccb5b5775f832fc7302002(
    *,
    start_hour: jsii.Number,
    days_of_week: typing.Optional[typing.Sequence[builtins.str]] = None,
    time_zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ef5c574f99738eadffd2c5203b5d7859d0f204f7e32b352c7382dd621b2d2eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcf8c184f5d530129f94ae7967e01c8ee91a7bd908b86127412063c5c4e10dd8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__586b6d27815c47c1150a06655ee5ec4413fe12ad40838b07be3bea518548f65f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d09bdda7e7d76f8c0c0023b5169a821dbe5ebc56a9bb80b96b3959ace55e7011(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551120e83a958de2a491b35a302fc87b3381660f18f95dee28eebf552610cec2(
    value: typing.Optional[PipelineRestartWindow],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b452b7e6bebe803bd3cca3b0b5e5278db4085c60b5dd7c4d4976f8ec60eaf5(
    *,
    service_principal_name: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2643619a09f82661aec1e1c79e6b2b2a836bc7d22161ea98677a37a4aa7dd084(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211304b79a4dffa799194b0cdf28972bb202e147bb69975b3e022a3f3969b2f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45bb5273aabad412146b5f151305fffd91cd37fdf0579eabe1687a52982919d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faa15c557c4b44abe8e1d01176999f496294b405ce8d6aa0eccf65984eebdc8f(
    value: typing.Optional[PipelineRunAs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d29c3e7df634a524db84f9a53d81f360f05c83c2ec781945dacda30bf99870f(
    *,
    default: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e6138e05ec93a75d7b4f682852e48e678e156b29ba62c26e91be52b6fe2832e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce2a0e7ccdfefb3633410370e0db3ad2b806ea247f04f6840b571828b8ec66b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9233c8fdd8e60986f1c4a536efc1c3d0ba0a28cf879ddc46c63c06f833ef0c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PipelineTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__271e32d0c972c04975b2ee92c62afec49ec6ac91cb5cecf8f44bd1cd83c9e62a(
    *,
    cron: typing.Optional[typing.Union[PipelineTriggerCron, typing.Dict[builtins.str, typing.Any]]] = None,
    manual: typing.Optional[typing.Union[PipelineTriggerManual, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3966946f020634493f35aa45fddfca6075af2b0675820ffa1a9aa1ea1891ea(
    *,
    quartz_cron_schedule: typing.Optional[builtins.str] = None,
    timezone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af87d2810d9ea58541714cd57e338795e8a5b5fa241df8c40caab0eddd1e4eb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b394f184f8ba5b9108ac5b1afb8247ac895577be21eec0aae58b751ba9b6059(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bd8f92aeaca56a9ff9cfc34a6ce67987709178d7e3cbb931a6fd9d27f1babc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5006399dcc1282a9dcdd9a4b62baec6f88ecd8c73f44ecacd0675bd5a8d61dc8(
    value: typing.Optional[PipelineTriggerCron],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524b872e03f68f6b8673f42f832d502e945ad7b4c184de23231d283bff82751c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33579b5f50a2aaff25d0a8a57cb1f682ec606552ab4df6758356070eb81c17da(
    value: typing.Optional[PipelineTriggerManual],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6644db1b269cf8893b6b595908b497243aead9d5b10332353d990fdb58ac2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24eba4b5fda8deeac8ce0db24da149fa91faf3b1933039eae9e4f78fcdfd5b87(
    value: typing.Optional[PipelineTrigger],
) -> None:
    """Type checking stubs"""
    pass
